/**
 * frontend/js/api.js
 * Cliente HTTP centralizado para as APIs REST do Previsor de Estoque.
 */

const API_BASE = '/api';

// Sistema de Notificacoes Corporativas Toast (sem emojis)
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
    const estilos = {
      sucesso: 'bg-emerald-900 text-white border-emerald-700',
      alerta: 'bg-amber-800 text-white border-amber-600',
      erro: 'bg-rose-900 text-white border-rose-700',
      info: 'bg-slate-900 text-white border-slate-700'
    };

    const tags = {
      sucesso: 'SUCESSO',
      alerta: 'ATENCAO',
      erro: 'ERRO',
      info: 'INFO'
    };

    toast.className = `p-3 rounded-lg shadow-lg border flex items-center gap-2.5 text-xs font-medium animate-slide-up ${estilos[tipo] || estilos.info}`;
    toast.innerHTML = `
      <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-white/20 tracking-wider">${tags[tipo] || 'INFO'}</span>
      <span class="flex-1">${mensagem}</span>
      <button class="opacity-60 hover:opacity-100 ml-2 text-xs font-bold" onclick="this.parentElement.remove()">✕</button>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(8px)';
      toast.style.transition = 'all 0.25s ease';
      setTimeout(() => toast.remove(), 250);
    }, 4000);
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

    const token = localStorage.getItem('previsor_token');
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
    const token = localStorage.getItem('previsor_token');
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
    const token = localStorage.getItem('previsor_token');
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
    const token = localStorage.getItem('previsor_token');
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
    const token = localStorage.getItem('previsor_token');
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
