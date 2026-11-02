/**
 * frontend/js/alertas.js
 * Módulo de Alertas Inteligentes e Ações de Reposição de Estoque.
 */

window.Alertas = {
  async carregar() {
    const tbody = document.getElementById('tabela-alertas-corpo');
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-slate-400">Verificando riscos de estoque...</td></tr>`;

    try {
      const alertas = await Api.get('/alertas', { horizonte_dias: 15 });

      if (!alertas || alertas.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="7" class="text-center py-10">
              <span class="text-3xl block mb-2">🎉</span>
              <p class="text-emerald-700 font-bold">Nenhum risco detectado!</p>
              <p class="text-xs text-slate-500">Todos os produtos estão com níveis saudáveis de cobertura de demanda.</p>
            </td>
          </tr>
        `;
        return;
      }

      tbody.innerHTML = '';
      alertas.forEach(a => {
        let badgeCls = 'badge-ruptura';
        let badgeIcon = '🚨';

        if (a.tipo_alerta === 'ATENCAO') {
          badgeCls = 'badge-atencao';
          badgeIcon = '⚠️';
        } else if (a.tipo_alerta === 'EXCESSO') {
          badgeCls = 'badge-excesso';
          badgeIcon = '📦';
        }

        const tr = document.createElement('tr');
        tr.className = 'border-b border-slate-100 hover:bg-slate-50 text-sm';
        tr.innerHTML = `
          <td class="py-3 px-4 font-semibold text-slate-900">${a.nome_produto}</td>
          <td class="py-3 px-4 text-xs text-slate-500">${a.categoria}</td>
          <td class="py-3 px-4 font-bold ${a.estoque_atual === 0 ? 'text-red-600' : 'text-slate-800'}">${a.estoque_atual} un</td>
          <td class="py-3 px-4 font-medium text-slate-700">${a.demanda_prevista_periodo} un (15d)</td>
          <td class="py-3 px-4 font-semibold ${a.dias_cobertura_estoque < 4 ? 'text-red-600' : 'text-slate-600'}">${a.dias_cobertura_estoque} dias</td>
          <td class="py-3 px-4"><span class="${badgeCls}">${badgeIcon} ${a.tipo_alerta}</span></td>
          <td class="py-3 px-4 text-right">
            ${a.tipo_alerta === 'RUPTURA' || a.tipo_alerta === 'ATENCAO' ? `
              <button onclick="window.Alertas.reporEstoque(${a.id_produto}, ${Math.ceil(a.quantidade_sugerida)})" class="text-xs bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-3 py-1.5 rounded-lg shadow-sm transition-all">
                Repor +${Math.ceil(a.quantidade_sugerida)} un
              </button>
            ` : `
              <button onclick="window.Alertas.sugerirPromocao('${a.nome_produto}', ${a.id_produto})" class="text-xs bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200 px-3 py-1.5 rounded-lg font-medium">
                Criar Promoção
              </button>
            `}
          </td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-red-500">Erro ao carregar alertas: ${err.message}</td></tr>`;
    }
  },

  async reporEstoque(idProduto, quantidade) {
    if (quantidade <= 0) quantidade = 20;

    const confirma = confirm(`Deseja simular a entrada imediata de +${quantidade} unidades deste produto no estoque do supermercado?`);
    if (!confirma) return;

    try {
      const resp = await Api.post(`/alertas/repor-estoque/${idProduto}`, { quantidade });
      alert(resp.mensagem);
      await this.carregar();
      if (window.Dashboard) window.Dashboard.carregar();
      if (window.Produtos) window.Produtos.carregarTabela();
    } catch (err) {
      alert('Erro ao repor estoque: ' + err.message);
    }
  },

  sugerirPromocao(nomeProduto, idProduto) {
    alert(`💡 Dica Estratégica Predikta:\nPara escoar o excesso de "${nomeProduto}", sugere-se campanha com 15% de desconto para elevar a elasticidade de saída e evitar perda por vencimento.`);
  }
};
