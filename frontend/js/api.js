/**
 * frontend/js/api.js
 * Cliente HTTP centralizado para as APIs REST do Predikta Data Solutions.
 */

const API_BASE = '/api';

// Sistema de Notificações Toast
window.Toast = {
  mostrar(mensagem, tipo = 'sucesso') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const cores = {
      sucesso: 'bg-emerald-800 text-white border-emerald-700',
      alerta: 'bg-amber-600 text-white border-amber-500',
      erro: 'bg-red-700 text-white border-red-600',
      info: 'bg-slate-800 text-white border-slate-700'
    };

    const icones = {
      sucesso: '✓',
      alerta: '⚠️',
      erro: '✕',
      info: 'ℹ️'
    };

    toast.className = `p-3.5 rounded-xl shadow-xl border flex items-center gap-3 text-xs font-medium animate-slide-up ${cores[tipo] || cores.info}`;
    toast.innerHTML = `
      <span class="text-sm font-bold">${icones[tipo] || '•'}</span>
      <span class="flex-1">${mensagem}</span>
      <button class="opacity-70 hover:opacity-100 ml-2" onclick="this.parentElement.remove()">✕</button>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4500);
  }
};

const Api = {
  async get(endpoint, params = {}) {
    const url = new URL(`${API_BASE}${endpoint}`, window.location.origin);
    Object.keys(params).forEach(k => {
      if (params[k] !== undefined && params[k] !== null && params[k] !== '') {
        url.searchParams.append(k, params[k]);
      }
    });

    const token = localStorage.getItem('predikta_token');
    const headers = { 'Accept': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(url.toString(), { headers });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Erro na requisição');
    }
    return res.json();
  },

  async post(endpoint, data = {}) {
    const token = localStorage.getItem('predikta_token');
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Erro na requisição');
    }
    return res.json();
  },

  async put(endpoint, data = {}) {
    const token = localStorage.getItem('predikta_token');
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Erro na requisição');
    }
    return res.json();
  },

  async delete(endpoint) {
    const token = localStorage.getItem('predikta_token');
    const headers = { 'Accept': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'DELETE',
      headers
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Erro na requisição');
    }
    return true;
  },

  async upload(endpoint, formData) {
    const token = localStorage.getItem('predikta_token');
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Erro no upload');
    }
    return res.json();
  }
};
