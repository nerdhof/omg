"""Compatibility shim for transformers.modeling_layers with transformers 4.50.0.

This module patches the missing transformers.modeling_layers module that peft 0.18.0
expects but which was removed in transformers 4.50.0.
"""

import sys
import types
import logging

logger = logging.getLogger(__name__)


def _create_modeling_layers_compat():
    """Create a compatibility shim for transformers.modeling_layers."""
    try:
        import transformers
        
        # Check if modeling_layers already exists
        if hasattr(transformers, 'modeling_layers'):
            return
        
        # Create a minimal compatibility class for GradientCheckpointingLayer
        # In transformers 4.50.0, this class was removed/refactored
        # peft 0.18.0 still expects it, so we provide a compatibility shim
        class GradientCheckpointingLayerCompat:
            """Compatibility shim for GradientCheckpointingLayer.
            
            This class provides a compatibility layer for peft 0.18.0 which
            expects transformers.modeling_layers.GradientCheckpointingLayer
            that was removed in transformers 4.50.0.
            """
            pass
        
        # Create a fake modeling_layers module
        modeling_layers_module = types.ModuleType('transformers.modeling_layers')
        modeling_layers_module.GradientCheckpointingLayer = GradientCheckpointingLayerCompat
        
        # Add it to transformers
        transformers.modeling_layers = modeling_layers_module
        
        # Also add it to sys.modules so imports work
        sys.modules['transformers.modeling_layers'] = modeling_layers_module
        
        logger.info("Created compatibility shim for transformers.modeling_layers")
        
    except ImportError:
        # transformers not installed yet, will be applied when it's imported
        pass
    except Exception as e:
        logger.warning(f"Failed to create modeling_layers compatibility shim: {e}")


# Apply the compatibility shim immediately when this module is imported
_create_modeling_layers_compat()

