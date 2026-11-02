/**
 * frontend/js/dashboard.js
 * Renderização dos indicadores, rankings e gráficos do Dashboard Executivo.
 */

window.Dashboard = {
  graficoVendasInstancia: null,
  graficoCategoriasInstancia: null,

  async carregar() {
    try {
      await Promise.all([
        this.carregarStats(),
        this.carregarGraficoVendas(),
        this.carregarGraficoCategorias(),
        this.carregarAlertasResumo()
      ]);
    } catch (err) {
      console.error('Erro ao carregar dashboard:', err);
    }
  },

  async carregarStats() {
    const stats = await Api.get('/dashboard/stats');

    document.getElementById('stat-total-produtos').textContent = stats.total_produtos;
    document.getElementById('stat-vendas-30d').textContent = Number(stats.total_vendas_30d).toLocaleString('pt-BR');
    document.getElementById('stat-receita-30d').textContent = `R$ ${stats.receita_estimada_30d.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    document.getElementById('stat-acuracia').textContent = `${stats.acuracia_media_modelo}%`;
    document.getElementById('stat-alertas-ruptura').textContent = stats.alertas_ruptura;
    document.getElementById('stat-alertas-excesso').textContent = stats.alertas_excesso;
    document.getElementById('stat-reducao-perdas').textContent = `${stats.reducao_estimada_perdas_pct}%`;

    // Renderiza Top 5 Produtos em Alta
    const containerAlta = document.getElementById('lista-produtos-alta');
    if (containerAlta) {
      if (!stats.produtos_em_alta || stats.produtos_em_alta.length === 0) {
        containerAlta.innerHTML = '<p class="text-xs text-slate-400 py-3">Sem dados preditivos suficientes.</p>';
      } else {
        containerAlta.innerHTML = stats.produtos_em_alta.map((p, i) => `
          <div class="flex items-center justify-between p-2.5 rounded-lg border border-slate-100 hover:bg-slate-50 transition-colors text-xs">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 font-bold flex items-center justify-center text-[10px]">${i + 1}</span>
              <div>
                <p class="font-semibold text-slate-800">${p.nome}</p>
                <p class="text-[10px] text-slate-400">${p.categoria}</p>
              </div>
            </div>
            <span class="font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded">${p.valor} un prev.</span>
          </div>
        `).join('');
      }
    }

    // Renderiza Top 5 Alertas Urgentes
    const containerUrgentes = document.getElementById('lista-alertas-urgentes');
    if (containerUrgentes) {
      if (!stats.alertas_urgentes || stats.alertas_urgentes.length === 0) {
        containerUrgentes.innerHTML = '<p class="text-xs text-emerald-600 py-3">Nenhum produto em risco imediato de falta.</p>';
      } else {
        containerUrgentes.innerHTML = stats.alertas_urgentes.map((a, i) => `
          <div class="flex items-center justify-between p-2.5 rounded-lg border border-red-100 bg-red-50/40 hover:bg-red-50 transition-colors text-xs">
            <div class="flex items-center gap-2">
              <span class="text-red-500 font-bold text-sm">⚠️</span>
              <div>
                <p class="font-semibold text-slate-800">${a.nome}</p>
                <p class="text-[10px] text-slate-500">${a.detalhe}</p>
              </div>
            </div>
            <button onclick="window.Navegacao.irParaAba('alertas')" class="text-[11px] font-semibold text-red-700 bg-red-100/70 hover:bg-red-200 px-2 py-1 rounded transition-colors">
              Resolver
            </button>
          </div>
        `).join('');
      }
    }
  },

  async carregarGraficoVendas() {
    const pontos = await Api.get('/dashboard/grafico-vendas');
    const ctx = document.getElementById('chart-vendas-evolucao').getContext('2d');

    const labels = pontos.map(p => p.label);
    const dadosReais = pontos.map(p => p.valor_real);
    const dadosPrevistos = pontos.map(p => p.valor_previsto);

    if (this.graficoVendasInstancia) {
      this.graficoVendasInstancia.destroy();
    }

    this.graficoVendasInstancia = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Vendas Reais Observadas',
            data: dadosReais,
            borderColor: '#059669',
            backgroundColor: 'rgba(5, 150, 105, 0.1)',
            borderWidth: 2.5,
            fill: true,
            tension: 0.35,
            pointRadius: 3,
            pointBackgroundColor: '#059669'
          },
          {
            label: 'Projeção Preditiva (Predikta)',
            data: dadosPrevistos,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.12)',
            borderWidth: 2.5,
            borderDash: [6, 4],
            fill: true,
            tension: 0.35,
            pointRadius: 4,
            pointBackgroundColor: '#3b82f6'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { font: { family: 'Inter', size: 12 }, boxWidth: 14 }
          },
          tooltip: {
            backgroundColor: '#0f172a',
            padding: 10,
            cornerRadius: 8,
            titleFont: { size: 13, weight: 'bold' }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: '#f1f5f9' },
            ticks: { font: { family: 'Inter', size: 11 } }
          },
          x: {
            grid: { display: false },
            ticks: { font: { family: 'Inter', size: 11 } }
          }
        }
      }
    });
  },

  async carregarGraficoCategorias() {
    const categorias = await Api.get('/dashboard/grafico-categorias');
    const ctx = document.getElementById('chart-categorias-rosca').getContext('2d');

    const labels = categorias.map(c => c.categoria);
    const valores = categorias.map(c => c.total_vendas);

    const cores = ['#059669', '#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ec4899'];

    if (this.graficoCategoriasInstancia) {
      this.graficoCategoriasInstancia.destroy();
    }

    this.graficoCategoriasInstancia = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: valores,
          backgroundColor: cores,
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { font: { family: 'Inter', size: 11 }, boxWidth: 12 }
          }
        },
        cutout: '68%'
      }
    });
  },

  async carregarAlertasResumo() {
    const alertas = await Api.get('/alertas', { horizonte_dias: 15 });
    const container = document.getElementById('lista-alertas-dashboard');
    container.innerHTML = '';

    if (!alertas || alertas.length === 0) {
      container.innerHTML = `
        <div class="p-4 text-sm text-emerald-700 bg-emerald-50 rounded-lg border border-emerald-200">
          Nenhum alerta crítico ativo. Todos os estoques operando dentro da margem segura.
        </div>
      `;
      return;
    }

    const alertasDestaque = alertas.slice(0, 4);
    alertasDestaque.forEach(a => {
      const isRuptura = a.tipo_alerta === 'RUPTURA';
      const badgeCls = isRuptura ? 'badge-ruptura' : (a.tipo_alerta === 'EXCESSO' ? 'badge-excesso' : 'badge-atencao');
      const badgeIcon = isRuptura ? '⚠️' : (a.tipo_alerta === 'EXCESSO' ? '📦' : '⏱️');

      const item = document.createElement('div');
      item.className = 'p-3 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 transition-colors flex items-center justify-between text-sm';
      item.innerHTML = `
        <div>
          <div class="flex items-center gap-2">
            <span class="font-semibold text-slate-800">${a.nome_produto}</span>
            <span class="${badgeCls}">${badgeIcon} ${a.tipo_alerta}</span>
          </div>
          <p class="text-xs text-slate-500 mt-1">${a.sugestao_acao}</p>
        </div>
        <button onclick="window.Navegacao.irParaAba('alertas')" class="text-xs font-medium text-emerald-600 hover:text-emerald-800 bg-emerald-50 px-2.5 py-1.5 rounded">
          Ver Ação
        </button>
      `;
      container.appendChild(item);
    });
  }
};
