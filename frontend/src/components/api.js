/**
 * ARTISTY API CLIENT - HTTP Request Helper
 * 
 * Provides a unified interface for making HTTP requests to the Artisty backend.
 * Handles environment-specific API endpoints and AWS Lambda path normalization.
 * 
 * Features:
 * - Environment variable support (VITE_API_BASE)
 * - AWS Lambda path normalization (strips /api prefix for AWS URLs)
 * - Automatic Content-Type headers for non-GET requests
 * - Fallback to local development server
 * 
 * @author Artisty Team
 * @version 2.0.0
 */

// Prefer environment variable, fall back to local development server
export const API_BASE = (import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000').replace(/\/$/, '');

// Ensure path starts with forward slash
const normalize = (p) => (p.startsWith('/') ? p : '/' + p);

// AWS Lambda doesn't need /api prefix in the actual path since API Gateway handles routing
const stripApiForAws = (p) =>
  API_BASE.includes('amazonaws.com') ? p.replace(/^\/api(\/|$)/, '/') : p;

/**
 * Make HTTP requests to the Artisty backend API
 * 
 * @param {string} path - API endpoint path (e.g., '/api/health')
 * @param {object} opts - Fetch options (method, headers, body, etc.)
 * @returns {Promise<Response>} - Fetch response promise
 */
export const apiFetch = (path, opts = {}) => {
  const finalPath = stripApiForAws(normalize(path));
  const url = `${API_BASE}${finalPath}`;
  const method = (opts.method || 'GET').toUpperCase();
  const headers = { ...(opts.headers || {}) };
  if (method !== 'GET' && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
  return fetch(url, { ...opts, headers });
};