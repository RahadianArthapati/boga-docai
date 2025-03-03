'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface FetchResult {
  method: string;
  url: string;
  status: number | null;
  statusText: string | null;
  error: string | null;
  data: any;
  duration: number;
  headers?: Record<string, string>;
}

export default function NetworkDebugPage() {
  const [results, setResults] = useState<FetchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [backendUrl, setBackendUrl] = useState<string>('');

  useEffect(() => {
    // Get the backend URL from environment variables
    const url = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000';
    setBackendUrl(url);
  }, []);

  const runTests = async () => {
    setLoading(true);
    setResults([]);
    
    try {
      // Test the base URL with fetch
      await testEndpoint('GET', `${backendUrl}/`, 'fetch');
      
      // Test the API endpoint with fetch
      await testEndpoint('GET', `${backendUrl}/api/v1/documents/list`, 'fetch');
      
      // Test the API endpoint with XMLHttpRequest
      await testEndpoint('GET', `${backendUrl}/api/v1/documents/list`, 'xhr');
      
      // Test with credentials
      await testEndpoint('GET', `${backendUrl}/api/v1/documents/list`, 'fetch-credentials');
      
      // Test with CORS mode
      await testEndpoint('GET', `${backendUrl}/api/v1/documents/list`, 'fetch-cors');
      
      // Test with no CORS
      await testEndpoint('GET', `${backendUrl}/api/v1/documents/list`, 'fetch-no-cors');
    } catch (error) {
      console.error('Error running tests:', error);
    } finally {
      setLoading(false);
    }
  };

  const testEndpoint = async (method: string, url: string, mode: string) => {
    const startTime = performance.now();
    const result: FetchResult = {
      method,
      url,
      status: null,
      statusText: null,
      error: null,
      data: null,
      duration: 0,
      headers: {}
    };
    
    try {
      let response;
      
      // Different test methods
      if (mode === 'fetch') {
        response = await fetch(url, { method });
      } else if (mode === 'fetch-credentials') {
        response = await fetch(url, { 
          method,
          credentials: 'include',
          headers: {
            'Accept': 'application/json'
          }
        });
      } else if (mode === 'fetch-cors') {
        response = await fetch(url, { 
          method,
          mode: 'cors',
          headers: {
            'Accept': 'application/json'
          }
        });
      } else if (mode === 'fetch-no-cors') {
        response = await fetch(url, { 
          method,
          mode: 'no-cors',
          headers: {
            'Accept': 'application/json'
          }
        });
        // no-cors doesn't allow accessing properties, so we just set a success status
        result.status = 200;
        result.statusText = 'OK (no-cors mode)';
        result.data = 'Response body not accessible in no-cors mode';
      } else if (mode === 'xhr') {
        // Use XMLHttpRequest
        response = await new Promise<any>((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          xhr.open(method, url);
          xhr.setRequestHeader('Accept', 'application/json');
          
          xhr.onload = function() {
            resolve({
              status: xhr.status,
              statusText: xhr.statusText,
              headers: {},
              text: async () => xhr.responseText,
              json: async () => JSON.parse(xhr.responseText)
            });
          };
          
          xhr.onerror = function() {
            reject(new Error('Network error'));
          };
          
          xhr.send();
        });
      }
      
      if (mode !== 'fetch-no-cors') {
        result.status = response.status;
        result.statusText = response.statusText;
        
        // Get headers
        if (response.headers) {
          response.headers.forEach((value: string, key: string) => {
            if (result.headers) {
              result.headers[key] = value;
            }
          });
        }
        
        // Try to get the response body
        try {
          const contentType = response.headers?.get('content-type');
          if (contentType?.includes('application/json')) {
            result.data = await response.json();
          } else {
            result.data = await response.text();
          }
        } catch (e) {
          result.data = 'Could not parse response body';
        }
      }
    } catch (error) {
      result.error = error instanceof Error ? error.message : String(error);
      console.error(`Error testing ${url}:`, error);
    } finally {
      result.duration = Math.round(performance.now() - startTime);
      setResults(prev => [...prev, {
        ...result, 
        method: `${method} (${mode})`,
      }]);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <div className="mb-4">
        <h1 className="text-2xl font-bold mb-2">Network Diagnostics</h1>
        <Link href="/debug" className="text-blue-500 hover:underline">← Back to Debug Home</Link>
      </div>
      
      <div className="mb-6">
        <p className="mb-2">Testing connection to backend at: <strong>{backendUrl}</strong></p>
        <button
          onClick={runTests}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition disabled:opacity-50"
        >
          {loading ? 'Running Tests...' : 'Run Network Tests'}
        </button>
      </div>
      
      {results.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Test Results</h2>
          
          <div className="grid gap-4">
            {results.map((result, index) => (
              <div key={index} className={`p-4 border rounded ${result.error ? 'border-red-300 bg-red-50' : 'border-green-300 bg-green-50'}`}>
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold">{result.method} {result.url}</h3>
                    <p>Completed in {result.duration}ms</p>
                  </div>
                  <div className={`px-2 py-1 rounded text-sm font-semibold ${result.error ? 'bg-red-200 text-red-800' : 'bg-green-200 text-green-800'}`}>
                    {result.error ? 'Error' : `${result.status} ${result.statusText}`}
                  </div>
                </div>
                
                {result.error && (
                  <div className="mt-2 p-2 bg-red-100 rounded">
                    <p className="font-mono text-sm">{result.error}</p>
                  </div>
                )}
                
                {result.headers && Object.keys(result.headers).length > 0 && (
                  <div className="mt-2">
                    <h4 className="font-semibold">Headers:</h4>
                    <pre className="text-xs bg-gray-100 p-2 rounded mt-1 overflow-auto max-h-20">
                      {JSON.stringify(result.headers, null, 2)}
                    </pre>
                  </div>
                )}
                
                {result.data && (
                  <div className="mt-2">
                    <h4 className="font-semibold">Response:</h4>
                    <pre className="text-xs bg-gray-100 p-2 rounded mt-1 overflow-auto max-h-40">
                      {typeof result.data === 'object' ? JSON.stringify(result.data, null, 2) : result.data}
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 