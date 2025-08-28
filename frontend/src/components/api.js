export const API_BASE = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '');

export const apiFetch = (path, opts) =>
  fetch(`${API_BASE}${path.startsWith('/') ? path : '/' + path}`, opts);