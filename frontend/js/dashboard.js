/**
 * frontend/js/dashboard.js
 * Renderização dos indicadores, rankings e gráficos do Painel Inicial.
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
      console.error('Erro ao carregar painel inicial:', err);
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

    // Renderiza Top 5 Produtos em Alta (sem emojis)
    const containerAlta = document.getElementById('lista-produtos-alta');
    if (containerAlta) {
      if (!stats.produtos_em_alta || stats.produtos_em_alta.length === 0) {
        containerAlta.innerHTML = '<p class="text-xs text-slate-500 py-3">Nenhum dado preditivo disponível. Cadastre produtos ou execute o preenchimento automático.</p>';
      } else {
        containerAlta.innerHTML = stats.produtos_em_alta.map((p, i) => `
          <div class="flex items-center justify-between p-2.5 rounded border border-slate-200 bg-white hover:bg-slate-50 transition-colors text-xs">
            <div class="flex items-center gap-2.5">
              <span class="w-5 h-5 rounded bg-slate-100 text-slate-700 font-bold flex items-center justify-center text-[10px] border border-slate-200">${i + 1}</span>
              <div>
                <p class="font-semibold text-slate-800">${p.nome}</p>
                <p class="text-[10px] text-slate-500">${p.categoria}</p>
              </div>
            </div>
            <span class="font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded text-[11px]">${p.valor} un prev.</span>
          </div>
        `).join('');
      }
    }

    // Renderiza Top 5 Alertas Urgentes (sem emojis)
    const containerUrgentes = document.getElementById('lista-alertas-urgentes');
    if (containerUrgentes) {
      if (!stats.alertas_urgentes || stats.alertas_urgentes.length === 0) {
        containerUrgentes.innerHTML = '<p class="text-xs text-emerald-700 py-3 font-medium">Nenhum produto em risco crítico de falta no momento.</p>';
      } else {
        containerUrgentes.innerHTML = stats.alertas_urgentes.map((a, i) => `
          <div class="flex items-center justify-between p-2.5 rounded border border-rose-200 bg-rose-50/50 hover:bg-rose-50 transition-colors text-xs">
            <div class="flex items-center gap-2.5">
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-200 text-rose-800 border border-rose-300">CRÍTICO</span>
              <div>
                <p class="font-semibold text-slate-800">${a.nome}</p>
                <p class="text-[10px] text-slate-600">${a.detalhe}</p>
              </div>
            </div>
            <button onclick="window.Navegacao.irParaAba('alertas')" class="text-[11px] font-semibold text-rose-700 hover:text-rose-900 bg-white border border-rose-200 px-2 py-1 rounded transition-colors">
              Repor
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
            label: 'Vendas Observadas (Histórico)',
            data: dadosReais,
            borderColor: '#0f766e',
            backgroundColor: 'rgba(15, 118, 110, 0.08)',
            borderWidth: 2,
            fill: true,
            tension: 0.3,
            pointRadius: 2.5,
            pointBackgroundColor: '#0f766e'
          },
          {
            label: 'Demanda Projetada (Modelo)',
            data: dadosPrevistos,
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37, 99, 235, 0.08)',
            borderWidth: 2,
            borderDash: [5, 4],
            fill: true,
            tension: 0.3,
            pointRadius: 3,
            pointBackgroundColor: '#2563eb'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { font: { family: 'Inter', size: 12 }, boxWidth: 12 }
          },
          tooltip: {
            backgroundColor: '#0f172a',
            padding: 8,
            cornerRadius: 4,
            titleFont: { size: 12, weight: 'bold' }
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

    const cores = ['#0f766e', '#0284c7', '#4f46e5', '#7c3aed', '#d97706', '#be123c'];

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
          borderWidth: 1.5,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { font: { family: 'Inter', size: 11 }, boxWidth: 10 }
          }
        },
        cutout: '65%'
      }
    });
  },

  async carregarAlertasResumo() {
    const alertas = await Api.get('/alertas', { horizonte_dias: 15 });
    const container = document.getElementById('lista-alertas-dashboard');
    container.innerHTML = '';

    if (!alertas || alertas.length === 0) {
      container.innerHTML = `
        <div class="p-3 text-xs text-slate-600 bg-slate-50 rounded border border-slate-200">
          Nenhum alerta crítico ativo. Todos os itens possuem cobertura regular para o período.
        </div>
      `;
      return;
    }

    const alertasDestaque = alertas.slice(0, 4);
    alertasDestaque.forEach(a => {
      const isRuptura = a.tipo_alerta === 'RUPTURA';
      const badgeCls = isRuptura ? 'badge-ruptura' : (a.tipo_alerta === 'EXCESSO' ? 'badge-excesso' : 'badge-atencao');

      const item = document.createElement('div');
      item.className = 'p-3 rounded border border-slate-200 bg-white hover:bg-slate-50 transition-colors flex items-center justify-between text-xs';
      item.innerHTML = `
        <div>
          <div class="flex items-center gap-2">
            <span class="font-semibold text-slate-800">${a.nome_produto}</span>
            <span class="${badgeCls}">${a.tipo_alerta}</span>
          </div>
          <p class="text-[11px] text-slate-500 mt-1">${a.sugestao_acao}</p>
        </div>
        <button onclick="window.Navegacao.irParaAba('alertas')" class="text-xs font-medium text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 px-2.5 py-1.5 rounded transition-colors">
          Detalhes
        </button>
      `;
      container.appendChild(item);
    });
  }
};
