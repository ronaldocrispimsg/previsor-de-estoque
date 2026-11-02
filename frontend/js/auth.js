/**
 * frontend/js/auth.js
 * Gerenciamento de login e sessão do gestor.
 */

const Auth = {
  init() {
    const loginForm = document.getElementById('login-form');
    const btnPreencherDemo = document.getElementById('btn-preencher-demo');
    const btnLogout = document.getElementById('btn-logout');

    if (btnPreencherDemo) {
      btnPreencherDemo.addEventListener('click', () => {
        document.getElementById('login-email').value = 'admin@admin.com';
        document.getElementById('login-senha').value = 'admin';
      });
    }

    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value.trim();
        const senha = document.getElementById('login-senha').value.trim();
        const errorAlert = document.getElementById('login-error');

        try {
          errorAlert.classList.add('hidden');
          const resp = await Api.post('/auth/login', { email, senha });
          localStorage.setItem('previsor_token', resp.token);
          localStorage.setItem('previsor_user', JSON.stringify(resp));
          this.mostrarApp();
        } catch (err) {
          errorAlert.textContent = err.message || 'Falha na autenticação';
          errorAlert.classList.remove('hidden');
        }
      });
    }

    if (btnLogout) {
      btnLogout.addEventListener('click', () => {
        localStorage.removeItem('previsor_token');
        localStorage.removeItem('previsor_user');
        this.mostrarLogin();
      });
    }

    if (localStorage.getItem('previsor_token')) {
      this.mostrarApp();
    } else {
      this.mostrarLogin();
    }
  },

  mostrarApp() {
    document.getElementById('tela-login').classList.add('hidden');
    document.getElementById('app-principal').classList.remove('hidden');

    const userRaw = localStorage.getItem('previsor_user');
    if (userRaw) {
      try {
        const u = JSON.parse(userRaw);
        document.getElementById('user-nome-topo').textContent = u.nome || 'admin';
        document.getElementById('user-cargo-topo').textContent = u.cargo || 'Administrador de Estoque';
      } catch (e) {}
    }

    if (window.Dashboard) {
      window.Dashboard.carregar();
    }
  },

  mostrarLogin() {
    document.getElementById('tela-login').classList.remove('hidden');
    document.getElementById('app-principal').classList.add('hidden');
  }
};
