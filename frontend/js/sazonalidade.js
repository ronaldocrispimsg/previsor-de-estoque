/**
 * frontend/js/sazonalidade.js
 * Módulo de Análise de Sazonalidade e Padrões Festivos do Varejo.
 */

window.Sazonalidade = {
  eventosCache: [],
  graficoCurvaAnualInstancia: null,

  async carregar() {
    try {
      this.eventosCache = await Api.get('/sazonalidade');
      this.renderizarBotoesEventos();
      if (this.eventosCache.length > 0) {
        this.selecionarEvento(this.eventosCache[0].id_evento);
      }
    } catch (err) {
      console.error('Erro ao carregar sazonalidades:', err);
    }
  },

  renderizarBotoesEventos() {
    const container = document.getElementById('botoes-eventos-sazonais');
    if (!container) return;

    container.innerHTML = this.eventosCache.map((ev, idx) => {
      return `
        <button onclick="window.Sazonalidade.selecionarEvento('${ev.id_evento}')" id="btn-ev-${ev.id_evento}" class="btn-evento-sazonal flex items-center justify-between p-3.5 rounded border border-slate-200 bg-white hover:border-slate-400 hover:shadow-sm transition-all text-left w-full ${idx === 0 ? 'border-emerald-700 ring-1 ring-emerald-700 bg-emerald-50/20' : ''}">
          <div>
            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500">${ev.periodo}</span>
            <h4 class="font-bold text-slate-900 text-xs mt-0.5">${ev.nome}</h4>
          </div>
          <span class="text-xs font-bold text-emerald-800 bg-emerald-100/70 border border-emerald-200 px-2 py-0.5 rounded">
            +${round((ev.multiplicador_medio - 1)*100)}%
          </span>
        </button>
      `;
    }).join('');
  },

  selecionarEvento(idEvento) {
    const evento = this.eventosCache.find(e => e.id_evento === idEvento);
    if (!evento) return;

    document.querySelectorAll('.btn-evento-sazonal').forEach(b => {
      b.classList.remove('border-emerald-700', 'ring-1', 'ring-emerald-700', 'bg-emerald-50/20');
    });
    const btnAtivo = document.getElementById(`btn-ev-${idEvento}`);
    if (btnAtivo) {
      btnAtivo.classList.add('border-emerald-700', 'ring-1', 'ring-emerald-700', 'bg-emerald-50/20');
    }

    document.getElementById('sazonal-nome').textContent = evento.nome;
    document.getElementById('sazonal-periodo').textContent = evento.periodo;
    document.getElementById('sazonal-descricao').textContent = evento.descricao;
    document.getElementById('sazonal-multiplicador').textContent = `+${Math.round((evento.multiplicador_medio - 1.0) * 100)}% de Pico Médio`;

    const elImpactoFinanceiro = document.getElementById('sazonal-impacto-financeiro');
    if (elImpactoFinanceiro) {
      elImpactoFinanceiro.textContent = `R$ ${evento.impacto_financeiro_potencial.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    }

    this.renderizarGraficoCurvaAnual(evento);

    const tbody = document.getElementById('tabela-sazonal-produtos');
    if (!tbody) return;

    if (!evento.produtos_impactados || evento.produtos_impactados.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-slate-500">Nenhum produto cadastrado diretamente sob as categorias deste evento festivo.</td></tr>`;
      return;
    }

    tbody.innerHTML = evento.produtos_impactados.map(p => {
      const isRisco = p.risco_sem_previsao.includes('Ruptura');
      const badgeCls = isRisco ? 'badge-ruptura' : 'badge-equilibrado';

      return `
        <tr class="border-b border-slate-100 hover:bg-slate-50 text-xs">
          <td class="py-3 px-4 font-semibold text-slate-800">${p.nome}</td>
          <td class="py-3 px-4 text-slate-500 text-[11px]">${p.categoria}</td>
          <td class="py-3 px-4 text-slate-600 font-medium">${p.demanda_normal_30d} un</td>
          <td class="py-3 px-4 text-emerald-800 font-bold">${p.demanda_pico_sazonal_30d} un (+${p.salto_demanda_pct}%)</td>
          <td class="py-3 px-4 font-semibold text-slate-800">${p.estoque_atual} un</td>
          <td class="py-3 px-4"><span class="${badgeCls}">${p.risco_sem_previsao}</span></td>
          <td class="py-3 px-4 text-right">
            ${p.compra_recomendada > 0 ? `
              <button onclick="window.Alertas.reporEstoque(${p.id_produto}, ${p.compra_recomendada})" class="text-xs bg-emerald-700 text-white hover:bg-emerald-800 px-3 py-1.5 rounded font-semibold transition-all">
                Repor +${p.compra_recomendada} un
              </button>
            ` : '<span class="text-xs text-slate-400">Estoque Suficiente</span>'}
          </td>
        </tr>
      `;
    }).join('');
  },

  renderizarGraficoCurvaAnual(evento) {
    const canvas = document.getElementById('chart-sazonalidade-anual');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const labels = evento.curva_anual_indices.map(m => m.mes_nome);
    const valores = evento.curva_anual_indices.map(m => m.indice);
    const cores = evento.curva_anual_indices.map(m => m.destaque ? '#0f766e' : '#cbd5e1');

    if (this.graficoCurvaAnualInstancia) {
      this.graficoCurvaAnualInstancia.destroy();
    }

    this.graficoCurvaAnualInstancia = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Índice de Demanda Sazonal (Base = 1.0)',
          data: valores,
          backgroundColor: cores,
          borderRadius: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(ctx) {
                const val = ctx.parsed.y;
                return `Multiplicador: x${val} (${val > 1.0 ? '+' + Math.round((val - 1)*100) + '%' : 'Regular'})`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: '#f1f5f9' },
            ticks: { font: { family: 'Inter', size: 10 } }
          },
          x: {
            grid: { display: false },
            ticks: { font: { family: 'Inter', size: 10 } }
          }
        }
      }
    });
  }
};

function round(val) {
  return Math.round(val);
}
