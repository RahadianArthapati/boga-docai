#!/usr/bin/env node

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const http = require('http');

// Get the frontend directory
const frontendDir = path.join(__dirname, 'frontend');

// Try to read backend URL from .env.local
let backendUrl = 'http://localhost:8000';
try {
  const envPath = path.join(frontendDir, '.env.local');
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf8');
    const match = envContent.match(/NEXT_PUBLIC_BACKEND_URL=(.+)/);
    if (match && match[1]) {
      backendUrl = match[1].trim();
      console.log(`Using backend URL from .env.local: ${backendUrl}`);
    }
  }
} catch (e) {
  console.error('Error reading .env.local file:', e);
}

// Function to check if backend is running
function checkBackendStatus() {
  return new Promise((resolve) => {
    // Parse the backend URL
    const url = new URL(backendUrl);
    const host = url.hostname;
    const port = url.port || (url.protocol === 'https:' ? 443 : 80);
    
    // Use a known API endpoint
    const apiPath = '/api/v1/documents/list';
    
    console.log(`Checking backend at ${host}:${port}${apiPath}...`);
    
    // Create a simple HTTP request to check if the backend is running
    const req = http.request(
      {
        host,
        port,
        path: apiPath,
        method: 'GET',
        timeout: 3000,
      },
      (res) => {
        console.log(`Backend status: ${res.statusCode}`);
        // Even a 404 response means the server is running
        if (res.statusCode >= 200 && res.statusCode < 500) {
          resolve(true);
        } else {
          resolve(false);
        }
      }
    );

    req.on('error', (error) => {
      console.error('Backend check error:', error.message);
      resolve(false);
    });

    req.on('timeout', () => {
      console.error('Backend request timed out');
      req.destroy();
      resolve(false);
    });

    req.end();
  });
}

// Function to start the backend
function startBackend() {
  console.log('Starting backend server...');
  
  try {
    // Try to kill any existing process on port 8000
    console.log('Attempting to kill any existing process on port 8000...');
    execSync('lsof -ti:8000 | xargs kill -9 || true');
  } catch (e) {
    // Ignore errors in killing process
    console.log('No existing process on port 8000 or could not kill it.');
  }

  // Get the url parts to determine if we're using a different port
  const url = new URL(backendUrl);
  const port = url.port || (url.protocol === 'https:' ? 443 : 80);
  
  console.log(`Starting Python backend on port ${port}...`);
  
  // Start the backend in detached mode
  const backendProcess = spawn('python', ['run_backend.py'], {
    detached: true,
    stdio: 'ignore',
    cwd: path.join(__dirname),
  });
  
  // Unref to allow the parent process to exit independently
  backendProcess.unref();
  
  // Give the backend some time to start
  console.log('Waiting for backend to start...');
  execSync('sleep 3');
}

// Main function
async function main() {
  try {
    console.log('Starting the application...');
    
    // Check if node_modules exist
    const nodeModulesPath = path.join(frontendDir, 'node_modules');
    if (!fs.existsSync(nodeModulesPath)) {
      console.log('Installing dependencies...');
      execSync('npm install', { cwd: frontendDir, stdio: 'inherit' });
    }
    
    // Check if .env.local exists, if not create it with default backend URL
    const envLocalPath = path.join(frontendDir, '.env.local');
    if (!fs.existsSync(envLocalPath)) {
      console.log('Creating .env.local with default backend URL...');
      fs.writeFileSync(envLocalPath, `NEXT_PUBLIC_BACKEND_URL=${backendUrl}\n`);
    }
    
    // Check if backend is running
    const isBackendRunning = await checkBackendStatus();
    
    if (!isBackendRunning) {
      console.log('Backend is not running.');
      startBackend();
    } else {
      console.log('Backend is already running.');
    }
    
    // Start the frontend
    console.log('Starting Next.js development server...');
    execSync('npm run dev', { cwd: frontendDir, stdio: 'inherit' });
    
  } catch (error) {
    console.error('Error starting the application:', error);
    process.exit(1);
  }
}

// Run the main function
main(); 