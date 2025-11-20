# Frontend

Vue.js frontend application for the music generation web app.

## Setup

1. Install dependencies:
```bash
npm install
```

## Running

Development server:
```bash
npm run dev
```

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Environment Variables

Create a `.env` file for local development:
```
VITE_API_URL=http://localhost:8000
```

For production builds, the `.env.production` file is used. To override the API URL:
- Create a `.env.production.local` file (not tracked by git), or
- Set the environment variable during build: `VITE_API_URL=https://api.example.com npm run build`

## Deployment

### GitHub Pages

This project is configured for automatic deployment to GitHub Pages using GitHub Actions.

#### Initial Setup (One-time)

1. Push your code to GitHub
2. Go to your repository's **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. The workflow will automatically deploy on every push to `main` branch that affects the `frontend/` directory

Your site will be available at: `https://nerdhof.github.io/omg/`

#### Manual Deployment

To manually trigger a deployment:
1. Go to **Actions** tab in your GitHub repository
2. Select the "Deploy Frontend to GitHub Pages" workflow
3. Click **Run workflow**

#### Backend CORS Configuration

**Important:** For the frontend to communicate with your backend API, you need to configure CORS on the backend to allow requests from your GitHub Pages domain.

Add the following to your backend's CORS allowed origins:
```
https://USERNAME.github.io
```

Replace `USERNAME` with your actual GitHub username.

If your backend is running locally:
- The deployed frontend will attempt to connect to `http://localhost:8000` by default
- This only works if you're accessing the site from the same machine running the backend
- For remote backend deployments, update the `VITE_API_URL` in `.env.production`

#### Custom Backend URL

To deploy with a different backend URL:

1. Before building, create `.env.production.local`:
```
VITE_API_URL=https://your-backend-api.com
```

2. Or modify the GitHub Actions workflow to set the environment variable during build

## Features

- Music generation form with style, topic, refrain, and text inputs
- Real-time job status polling
- Audio player for generated versions
- Download functionality
- Responsive design

