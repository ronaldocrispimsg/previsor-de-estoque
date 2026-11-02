/**
 * frontend/js/alertas.js
 * Módulo de Alertas Inteligentes e Ações de Reposição de Estoque.
 */

window.Alertas = {
  async carregar() {
    const tbody = document.getElementById('tabela-alertas-corpo');
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-slate-400">Verificando cobertura de estoque...</td></tr>`;

    try {
      const alertas = await Api.get('/alertas', { horizonte_dias: 15 });

      if (!alertas || alertas.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="8" class="text-center py-8">
              <p class="text-emerald-800 font-bold text-sm">Nenhum risco de estoque detectado.</p>
              <p class="text-xs text-slate-500 mt-1">Todos os itens apresentam cobertura satisfatória para o horizonte projetado.</p>
            </td>
          </tr>
        `;
        return;
      }

      tbody.innerHTML = '';
      alertas.forEach(a => {
        let badgeCls = 'badge-ruptura';

        if (a.tipo_alerta === 'ATENCAO') {
          badgeCls = 'badge-atencao';
        } else if (a.tipo_alerta === 'EXCESSO') {
          badgeCls = 'badge-excesso';
        }

        const impactoFmt = a.impacto_financeiro_estimado > 0 ?
          `R$ ${a.impacto_financeiro_estimado.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}` : '--';

        const tr = document.createElement('tr');
        tr.className = 'border-b border-slate-100 hover:bg-slate-50 text-xs';
        tr.innerHTML = `
          <td class="py-3 px-4 font-semibold text-slate-900">${a.nome_produto}</td>
          <td class="py-3 px-4 text-slate-500">${a.categoria}</td>
          <td class="py-3 px-4 font-bold ${a.estoque_atual === 0 ? 'text-rose-700' : 'text-slate-800'}">${a.estoque_atual} un</td>
          <td class="py-3 px-4 font-medium text-slate-700">${a.demanda_prevista_periodo} un (15d)</td>
          <td class="py-3 px-4 font-semibold ${a.dias_cobertura_estoque < 4 ? 'text-rose-700' : 'text-slate-600'}">${a.dias_cobertura_estoque} dias</td>
          <td class="py-3 px-4 font-bold ${a.tipo_alerta === 'EXCESSO' ? 'text-indigo-700' : 'text-rose-700'}">${impactoFmt}</td>
          <td class="py-3 px-4"><span class="${badgeCls}">${a.tipo_alerta}</span></td>
          <td class="py-3 px-4 text-right">
            ${a.tipo_alerta === 'RUPTURA' || a.tipo_alerta === 'ATENCAO' ? `
              <button onclick="window.Alertas.reporEstoque(${a.id_produto}, ${Math.ceil(a.quantidade_sugerida)})" class="text-xs bg-emerald-700 hover:bg-emerald-800 text-white font-semibold px-3 py-1.5 rounded transition-all">
                Repor +${Math.ceil(a.quantidade_sugerida)} un
              </button>
            ` : `
              <button onclick="window.Alertas.sugerirPromocao('${a.nome_produto}', ${a.id_produto})" class="text-xs bg-indigo-50 text-indigo-800 hover:bg-indigo-100 border border-indigo-200 px-3 py-1.5 rounded font-medium">
                Sugerir Promoção
              </button>
            `}
          </td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-rose-700">Erro ao carregar alertas: ${err.message}</td></tr>`;
    }
  },

  async reporEstoque(idProduto, quantidade) {
    if (quantidade <= 0) quantidade = 20;

    const confirma = confirm(`Confirmar entrada de +${quantidade} unidades deste produto no estoque?`);
    if (!confirma) return;

    try {
      const resp = await Api.post(`/alertas/repor-estoque/${idProduto}`, { quantidade });
      window.Toast.mostrar(resp.mensagem, 'sucesso');
      await this.carregar();
      if (window.Dashboard) window.Dashboard.carregar();
      if (window.Produtos) window.Produtos.carregarTabela();
    } catch (err) {
      window.Toast.mostrar('Erro ao repor estoque: ' + err.message, 'erro');
    }
  },

  sugerirPromocao(nomeProduto, idProduto) {
    window.Toast.mostrar(
      `Recomendação: Para acelerar o escoamento de "${nomeProduto}", cadastre uma campanha com desconto na aba Vendas.`,
      'info'
    );
  }
};
