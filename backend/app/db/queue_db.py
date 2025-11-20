"""SQLite database for persisting generation job queue."""

import sqlite3
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class QueueDatabase:
    """SQLite database for persisting job queue state."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the queue database.
        
        Args:
            db_path: Path to SQLite database file. If None, uses QUEUE_DB_PATH env var
                    or defaults to './data/queue.db'
        """
        if db_path is None:
            db_path = os.environ.get("QUEUE_DB_PATH", "./data/queue.db")
        
        self.db_path = Path(db_path)
        
        # Create parent directory if it doesn't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
        
        logger.info(f"Initialized queue database at {self.db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with WAL mode enabled."""
        conn = sqlite3.Connection(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        
        return conn
    
    def _init_db(self):
        """Initialize database schema."""
        conn = self._get_connection()
        try:
            # Create jobs table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    lyrics TEXT,
                    duration REAL NOT NULL,
                    num_versions INTEGER NOT NULL,
                    seed INTEGER,
                    provider TEXT,
                    status TEXT NOT NULL,
                    progress REAL DEFAULT 0.0,
                    error TEXT,
                    versions TEXT,  -- JSON array
                    version_paths TEXT,  -- JSON object mapping version_id to audio_path
                    model_service_job_id TEXT,
                    created_at TEXT NOT NULL,
                    cancelled INTEGER DEFAULT 0
                )
            """)
            
            # Create queue table for maintaining order
            conn.execute("""
                CREATE TABLE IF NOT EXISTS queue (
                    position INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL UNIQUE,
                    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_queue_job_id ON queue(job_id)")
            
            conn.commit()
            logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def save_job(self, job: Dict[str, Any]) -> bool:
        """
        Save or update a job in the database.
        
        Args:
            job: Job dictionary with all fields
            
        Returns:
            True if successful
        """
        conn = self._get_connection()
        try:
            # Serialize complex fields to JSON
            versions_json = None
            if job.get("versions"):
                # Convert VersionInfo objects to dicts if needed
                versions_list = []
                for v in job["versions"]:
                    if hasattr(v, "model_dump"):
                        versions_list.append(v.model_dump())
                    elif hasattr(v, "dict"):
                        versions_list.append(v.dict())
                    else:
                        versions_list.append(v)
                versions_json = json.dumps(versions_list)
            
            version_paths_json = None
            if job.get("version_paths"):
                version_paths_json = json.dumps(job["version_paths"])
            
            # Convert datetime to ISO string
            created_at = job["created_at"]
            if isinstance(created_at, datetime):
                created_at = created_at.isoformat()
            
            conn.execute("""
                INSERT OR REPLACE INTO jobs (
                    job_id, prompt, lyrics, duration, num_versions, seed, provider,
                    status, progress, error, versions, version_paths, model_service_job_id,
                    created_at, cancelled
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job["job_id"],
                job["prompt"],
                job.get("lyrics"),
                job["duration"],
                job["num_versions"],
                job.get("seed"),
                job.get("provider"),
                job["status"].value if hasattr(job["status"], "value") else job["status"],
                job.get("progress", 0.0),
                job.get("error"),
                versions_json,
                version_paths_json,
                job.get("model_service_job_id"),
                created_at,
                1 if job.get("cancelled", False) else 0
            ))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save job {job.get('job_id')}: {e}", exc_info=True)
            return False
        finally:
            conn.close()
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job dictionary or None if not found
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM jobs WHERE job_id = ?",
                (job_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return self._row_to_job(row)
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}", exc_info=True)
            return None
        finally:
            conn.close()
    
    def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update specific fields of a job.
        
        Args:
            job_id: Job ID
            updates: Dictionary of fields to update
            
        Returns:
            True if successful
        """
        if not updates:
            return True
        
        conn = self._get_connection()
        try:
            # Build UPDATE query dynamically
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key == "status":
                    value = value.value if hasattr(value, "value") else value
                elif key in ("versions", "version_paths") and value is not None:
                    # Serialize to JSON
                    if key == "versions":
                        versions_list = []
                        for v in value:
                            if hasattr(v, "model_dump"):
                                versions_list.append(v.model_dump())
                            elif hasattr(v, "dict"):
                                versions_list.append(v.dict())
                            else:
                                versions_list.append(v)
                        value = json.dumps(versions_list)
                    else:
                        value = json.dumps(value)
                elif key == "cancelled":
                    value = 1 if value else 0
                
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            values.append(job_id)
            
            query = f"UPDATE jobs SET {', '.join(set_clauses)} WHERE job_id = ?"
            conn.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {e}", exc_info=True)
            return False
        finally:
            conn.close()
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job from the database.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if successful
        """
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}", exc_info=True)
            return False
        finally:
            conn.close()
    
    def get_all_jobs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all jobs from the database.
        
        Returns:
            Dictionary mapping job_id to job data
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT * FROM jobs")
            rows = cursor.fetchall()
            
            jobs = {}
            for row in rows:
                job = self._row_to_job(row)
                jobs[job["job_id"]] = job
            
            return jobs
        except Exception as e:
            logger.error(f"Failed to get all jobs: {e}", exc_info=True)
            return {}
        finally:
            conn.close()
    
    def add_to_queue(self, job_id: str) -> bool:
        """
        Add a job to the queue.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if successful
        """
        conn = self._get_connection()
        try:
            conn.execute("INSERT INTO queue (job_id) VALUES (?)", (job_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to add job {job_id} to queue: {e}", exc_info=True)
            return False
        finally:
            conn.close()
    
    def remove_from_queue(self, job_id: str) -> bool:
        """
        Remove a job from the queue.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if successful
        """
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM queue WHERE job_id = ?", (job_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id} from queue: {e}", exc_info=True)
            return False
        finally:
            conn.close()
    
    def get_queue(self) -> List[str]:
        """
        Get the queue in order.
        
        Returns:
            List of job IDs in queue order
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT job_id FROM queue ORDER BY position ASC"
            )
            rows = cursor.fetchall()
            return [row["job_id"] for row in rows]
        except Exception as e:
            logger.error(f"Failed to get queue: {e}", exc_info=True)
            return []
        finally:
            conn.close()
    
    def reorder_queue(self, job_id: str, new_position: int) -> bool:
        """
        Move a job to a new position in the queue.
        
        Args:
            job_id: Job ID to move
            new_position: New position (1-based)
            
        Returns:
            True if successful
        """
        conn = self._get_connection()
        try:
            # Get current queue
            cursor = conn.execute(
                "SELECT job_id FROM queue ORDER BY position ASC"
            )
            queue = [row["job_id"] for row in cursor.fetchall()]
            
            if job_id not in queue:
                return False
            
            # Remove job from current position
            queue.remove(job_id)
            
            # Insert at new position (convert to 0-based)
            queue.insert(new_position - 1, job_id)
            
            # Clear queue table and rebuild with new order
            conn.execute("DELETE FROM queue")
            
            for idx, jid in enumerate(queue, start=1):
                conn.execute(
                    "INSERT INTO queue (position, job_id) VALUES (?, ?)",
                    (idx, jid)
                )
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to reorder queue for job {job_id}: {e}", exc_info=True)
            return False
        finally:
            conn.close()
    
    def _row_to_job(self, row: sqlite3.Row) -> Dict[str, Any]:
        """
        Convert a database row to a job dictionary.
        
        Args:
            row: Database row
            
        Returns:
            Job dictionary
        """
        job = {
            "job_id": row["job_id"],
            "prompt": row["prompt"],
            "lyrics": row["lyrics"],
            "duration": row["duration"],
            "num_versions": row["num_versions"],
            "seed": row["seed"],
            "provider": row["provider"],
            "status": row["status"],  # Will be converted to enum in JobManager
            "progress": row["progress"],
            "error": row["error"],
            "versions": None,
            "version_paths": None,
            "model_service_job_id": row["model_service_job_id"],
            "created_at": datetime.fromisoformat(row["created_at"]),
            "cancelled": bool(row["cancelled"]),
            "task": None,  # Not persisted
            "queue_position": 0  # Will be set by JobManager
        }
        
        # Deserialize JSON fields
        if row["versions"]:
            try:
                job["versions"] = json.loads(row["versions"])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse versions JSON for job {row['job_id']}")
        
        if row["version_paths"]:
            try:
                job["version_paths"] = json.loads(row["version_paths"])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse version_paths JSON for job {row['job_id']}")
        
        return job

