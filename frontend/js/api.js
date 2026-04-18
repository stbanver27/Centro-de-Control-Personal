/* ── api.js — centralized HTTP client ───────────────────────── */

const BASE = '/api';

function getToken() {
  return localStorage.getItem('controlos_token');
}

function setToken(token) {
  localStorage.setItem('controlos_token', token);
}

function clearToken() {
  localStorage.removeItem('controlos_token');
  localStorage.removeItem('controlos_user');
}

function redirectLogin() {
  clearToken();
  window.location.href = '/';
}

async function request(method, path, body = null, params = null) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let url = BASE + path;
  if (params) {
    const qs = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v != null))
    ).toString();
    if (qs) url += '?' + qs;
  }

  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  if (res.status === 401) { redirectLogin(); return; }

  if (res.status === 204) return null;

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const msg = data?.detail || `HTTP ${res.status}`;
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }

  return data;
}

const api = {
  get:    (path, params)       => request('GET',    path, null, params),
  post:   (path, body)         => request('POST',   path, body),
  patch:  (path, body)         => request('PATCH',  path, body),
  delete: (path)               => request('DELETE', path),

  // Auth
  login:   (email, password)   => api.post('/auth/login', { email, password }),
  me:      ()                  => api.get('/auth/me'),

  // Dashboard
  dashboard: ()                => api.get('/dashboard'),

  // Finance
  categories:      ()          => api.get('/finance/categories'),
  transactions:    (params)    => api.get('/finance/transactions', params),
  createTx:        (body)      => api.post('/finance/transactions', body),
  deleteTx:        (id)        => api.delete(`/finance/transactions/${id}`),
  summary:         (params)    => api.get('/finance/summary', params),
  categorySummary: (params)    => api.get('/finance/summary/categories', params),
  balance:         ()          => api.get('/finance/balance'),

  // Projects
  projects:        ()          => api.get('/projects'),
  project:         (id)        => api.get(`/projects/${id}`),
  createProject:   (body)      => api.post('/projects', body),
  updateProject:   (id, body)  => api.patch(`/projects/${id}`, body),
  deleteProject:   (id)        => api.delete(`/projects/${id}`),
  createTask:      (pid, body) => api.post(`/projects/${pid}/tasks`, body),
  updateTask:      (id, body)  => api.patch(`/projects/tasks/${id}`, body),
  deleteTask:      (id)        => api.delete(`/projects/tasks/${id}`),
};

/* ── toast ──────────────────────────────────────────────────── */
function toast(msg, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3200);
}

/* ── format helpers ─────────────────────────────────────────── */
function fmtCLP(n) {
  return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(n);
}

function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('es-CL', { day: '2-digit', month: 'short', year: 'numeric' });
}

function fmtShortDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return `${d.getDate()} ${d.toLocaleString('es-CL', { month: 'short' })}`;
}

function amountClass(type) {
  return type === 'income' ? 'amount-positive' : 'amount-negative';
}

function amountSign(type, amount) {
  return (type === 'income' ? '+' : '-') + fmtCLP(amount);
}

const PRIORITY_LABEL = { high: 'Alta', medium: 'Media', low: 'Baja' };
const STATUS_LABEL = { pending: 'Pendiente', in_progress: 'En progreso', done: 'Terminado' };

function priorityBadge(p) {
  return `<span class="badge badge-${p}">${PRIORITY_LABEL[p] || p}</span>`;
}

function statusBadge(s) {
  const cls = s === 'in_progress' ? 'progress' : s;
  return `<span class="badge badge-${cls}">${STATUS_LABEL[s] || s}</span>`;
}

/* ── auth guard ─────────────────────────────────────────────── */
async function requireAuth() {
  if (!getToken()) { redirectLogin(); return null; }
  try {
    const user = await api.me();
    localStorage.setItem('controlos_user', JSON.stringify(user));
    return user;
  } catch {
    redirectLogin();
    return null;
  }
}

function renderTopbar(user) {
  const initial = user?.name?.[0]?.toUpperCase() || 'U';
  document.querySelectorAll('[data-user-initial]').forEach(el => el.textContent = initial);
  document.querySelectorAll('[data-user-name]').forEach(el => el.textContent = user?.name || '');
  document.querySelectorAll('[data-logout]').forEach(el => {
    el.addEventListener('click', () => { clearToken(); window.location.href = '/'; });
  });
}

function setActiveNav(path) {
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.toggle('active', link.getAttribute('href') === path);
  });
}
