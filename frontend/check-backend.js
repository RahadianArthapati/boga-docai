#!/usr/bin/env node

const http = require('http');
const fs = require('fs');
const path = require('path');

// Try to read backend URL from .env.local
let backendUrl = 'http://127.0.0.1:8000';
try {
  const envPath = path.join(__dirname, '.env.local');
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
      console.log('Backend is running.');
      process.exit(0);
    } else {
      console.error('Backend returned error status:', res.statusCode);
      process.exit(1);
    }
  }
);

req.on('error', (error) => {
  console.error('Backend check error:', error.message);
  process.exit(1);
});

req.on('timeout', () => {
  console.error('Backend request timed out');
  req.destroy();
  process.exit(1);
});

req.end(); 