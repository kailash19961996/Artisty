// Prefer env var; fall back to local Flask during dev
export const API_BASE = (import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000').replace(/\/$/, '');

const normalize = (p) => (p.startsWith('/') ? p : '/' + p);
const stripApiForAws = (p) =>
  API_BASE.includes('amazonaws.com') ? p.replace(/^\/api(\/|$)/, '/') : p;

export const apiFetch = (path, opts = {}) => {
  const finalPath = stripApiForAws(normalize(path));
  const url = `${API_BASE}${finalPath}`;
  return fetch(url, { ...opts, headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) }});
};