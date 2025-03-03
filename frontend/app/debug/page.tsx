'use client';

import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

export default function DebugPage() {
  const [backendInfo, setBackendInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [healthCheckResult, setHealthCheckResult] = useState<any>(null);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        setLoading(true);
        // Get backend configuration info
        const infoResult = await apiService.getBackendInfo();
        setBackendInfo(infoResult.info);
        
        // Also run the health check
        const healthResult = await apiService.checkBackendStatus();
        setHealthCheckResult(healthResult);
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
        console.error('Debug page error:', err);
      } finally {
        setLoading(false);
      }
    };
    
    checkBackend();
  }, []);

  // Function to refresh the checks
  const handleRefresh = () => {
    setLoading(true);
    setError(null);
    setBackendInfo(null);
    setHealthCheckResult(null);
    
    // Re-trigger the useEffect
    setTimeout(() => {
      // Force React to re-run the effect
      setLoading(true);
    }, 100);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Backend Connection Debug</h1>
      
      <div className="mb-4 flex gap-2">
        <button
          onClick={handleRefresh}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
          disabled={loading}
        >
          {loading ? 'Checking...' : 'Refresh'}
        </button>
        
        <a 
          href="/debug/network"
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition inline-block"
        >
          Advanced Network Diagnostics
        </a>
      </div>
      
      {error && (
        <div className="p-4 mb-4 bg-red-100 border border-red-400 text-red-700 rounded">
          <h2 className="font-bold">Error</h2>
          <p>{error}</p>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Health Check Results */}
        <div className="p-4 border rounded shadow">
          <h2 className="text-xl font-semibold mb-2">Health Check</h2>
          
          {loading ? (
            <p>Loading health check results...</p>
          ) : healthCheckResult ? (
            <div>
              <div className={`p-2 rounded ${healthCheckResult.success ? 'bg-green-100' : 'bg-red-100'}`}>
                <p className="font-bold">
                  Status: {healthCheckResult.success ? 'Success' : 'Failed'}
                </p>
                <p>
                  {healthCheckResult.message || healthCheckResult.error || 'No message'}
                </p>
              </div>
              
              <div className="mt-2">
                <p className="font-mono text-sm overflow-auto max-h-40 bg-gray-100 p-2 rounded">
                  {JSON.stringify(healthCheckResult, null, 2)}
                </p>
              </div>
            </div>
          ) : (
            <p>No health check results available</p>
          )}
        </div>
        
        {/* Backend Configuration */}
        <div className="p-4 border rounded shadow">
          <h2 className="text-xl font-semibold mb-2">Backend Configuration</h2>
          
          {loading ? (
            <p>Loading configuration...</p>
          ) : backendInfo ? (
            <div>
              <ul className="space-y-1">
                <li><strong>Base URL:</strong> {backendInfo.baseURL}</li>
                <li><strong>API URL:</strong> {backendInfo.apiURL}</li>
                <li><strong>Documents URL:</strong> {backendInfo.documentsURL}</li>
                <li><strong>Environment:</strong> {backendInfo.nodeEnv}</li>
                <li><strong>NEXT_PUBLIC_BACKEND_URL:</strong> {backendInfo.backendUrl}</li>
                <li><strong>Running in:</strong> {backendInfo.browser ? 'Browser' : 'Server'}</li>
              </ul>
            </div>
          ) : (
            <p>No configuration available</p>
          )}
        </div>
        
        {/* Connection Test Results */}
        <div className="col-span-1 md:col-span-2 p-4 border rounded shadow">
          <h2 className="text-xl font-semibold mb-2">Connection Test</h2>
          
          {loading ? (
            <p>Testing connection...</p>
          ) : backendInfo?.connectionTest ? (
            <div>
              <div className={`p-2 rounded ${backendInfo.connectionTest.status === 'completed' && !backendInfo.connectionTest.error ? 'bg-green-100' : 'bg-red-100'}`}>
                <p className="font-bold">
                  Status: {backendInfo.connectionTest.status}
                  {backendInfo.connectionTest.error && ` - Error: ${backendInfo.connectionTest.error}`}
                </p>
              </div>
              
              <div className="mt-2">
                <h3 className="font-semibold">Details:</h3>
                <pre className="font-mono text-sm overflow-auto max-h-96 bg-gray-100 p-2 rounded">
                  {JSON.stringify(backendInfo.connectionTest.details, null, 2)}
                </pre>
              </div>
            </div>
          ) : (
            <p>No connection test results available</p>
          )}
        </div>
      </div>
    </div>
  );
} 