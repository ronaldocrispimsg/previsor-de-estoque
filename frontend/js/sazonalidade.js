/**
 * frontend/js/sazonalidade.js
 * Módulo de Análise de Sazonalidade e Padrões Festivos (Predikta).
 */

window.Sazonalidade = {
  eventosCache: [],

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
      let icon = '🍫';
      if (ev.id_evento === 'festa_junina') icon = '🌽';
      if (ev.id_evento === 'verao') icon = '☀️';
      if (ev.id_evento === 'natal') icon = '🎄';

      return `
        <button onclick="window.Sazonalidade.selecionarEvento('${ev.id_evento}')" id="btn-ev-${ev.id_evento}" class="btn-evento-sazonal flex items-center gap-3 p-4 rounded-xl border border-slate-200 bg-white hover:border-emerald-500 hover:shadow-sm transition-all text-left w-full ${idx === 0 ? 'border-emerald-600 ring-2 ring-emerald-100 bg-emerald-50/30' : ''}">
          <span class="text-2xl">${icon}</span>
          <div>
            <h4 class="font-bold text-slate-800 text-sm">${ev.nome}</h4>
            <p class="text-xs text-slate-500">${ev.periodo} • Multiplicador Médio: <strong class="text-emerald-700 font-semibold">+${round((ev.multiplicador_medio - 1)*100)}%</strong></p>
          </div>
        </button>
      `;
    }).join('');
  },

  selecionarEvento(idEvento) {
    const evento = this.eventosCache.find(e => e.id_evento === idEvento);
    if (!evento) return;

    // Atualiza classes ativas
    document.querySelectorAll('.btn-evento-sazonal').forEach(b => {
      b.classList.remove('border-emerald-600', 'ring-2', 'ring-emerald-100', 'bg-emerald-50/30');
    });
    const btnAtivo = document.getElementById(`btn-ev-${idEvento}`);
    if (btnAtivo) {
      btnAtivo.classList.add('border-emerald-600', 'ring-2', 'ring-emerald-100', 'bg-emerald-50/30');
    }

    document.getElementById('sazonal-nome').textContent = evento.nome;
    document.getElementById('sazonal-periodo').textContent = evento.periodo;
    document.getElementById('sazonal-descricao').textContent = evento.descricao;
    document.getElementById('sazonal-multiplicador').textContent = `+${Math.round((evento.multiplicador_medio - 1.0) * 100)}% de Demanda Estimada`;

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
        <tr class="border-b border-slate-100 hover:bg-slate-50 text-sm">
          <td class="py-3 px-4 font-semibold text-slate-800">${p.nome}</td>
          <td class="py-3 px-4 text-slate-500 text-xs">${p.categoria}</td>
          <td class="py-3 px-4 text-slate-600 font-medium">${p.demanda_normal_30d} un</td>
          <td class="py-3 px-4 text-emerald-700 font-bold">${p.demanda_pico_sazonal_30d} un (+${p.salto_demanda_pct}%)</td>
          <td class="py-3 px-4 font-semibold text-slate-800">${p.estoque_atual} un</td>
          <td class="py-3 px-4"><span class="${badgeCls}">${p.risco_sem_previsao}</span></td>
          <td class="py-3 px-4 text-right">
            ${p.compra_recomendada > 0 ? `
              <button onclick="window.Alertas.reporEstoque(${p.id_produto}, ${p.compra_recomendada})" class="text-xs bg-emerald-600 text-white hover:bg-emerald-700 px-3 py-1.5 rounded-lg font-semibold shadow-sm transition-all">
                Antecipar +${p.compra_recomendada} un
              </button>
            ` : '<span class="text-xs text-slate-400">Estoque Suficiente</span>'}
          </td>
        </tr>
      `;
    }).join('');
  }
};

function round(val) {
  return Math.round(val);
}
