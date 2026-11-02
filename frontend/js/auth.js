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
        document.getElementById('login-email').value = 'gestor@supermercado.com';
        document.getElementById('login-senha').value = 'admin123';
      });
    }

    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const senha = document.getElementById('login-senha').value;
        const errorAlert = document.getElementById('login-error');

        try {
          errorAlert.classList.add('hidden');
          const resp = await Api.post('/auth/login', { email, senha });
          localStorage.setItem('predikta_token', resp.token);
          localStorage.setItem('predikta_user', JSON.stringify(resp));
          this.mostrarApp();
        } catch (err) {
          errorAlert.textContent = err.message || 'Falha no login';
          errorAlert.classList.remove('hidden');
        }
      });
    }

    if (btnLogout) {
      btnLogout.addEventListener('click', () => {
        localStorage.removeItem('predikta_token');
        localStorage.removeItem('predikta_user');
        this.mostrarLogin();
      });
    }

    // Checa sessão existente
    if (localStorage.getItem('predikta_token')) {
      this.mostrarApp();
    } else {
      this.mostrarLogin();
    }
  },

  mostrarApp() {
    document.getElementById('tela-login').classList.add('hidden');
    document.getElementById('app-principal').classList.remove('hidden');

    const userRaw = localStorage.getItem('predikta_user');
    if (userRaw) {
      try {
        const u = JSON.parse(userRaw);
        document.getElementById('user-nome-topo').textContent = u.nome;
        document.getElementById('user-cargo-topo').textContent = u.cargo;
      } catch (e) {}
    }

    // Carrega o dashboard inicial
    if (window.Dashboard) {
      window.Dashboard.carregar();
    }
  },

  mostrarLogin() {
    document.getElementById('tela-login').classList.remove('hidden');
    document.getElementById('app-principal').classList.add('hidden');
  }
};
