/**
 * frontend/js/vendas.js
 * Módulo de Histórico e Ingestão de Vendas.
 */

window.Vendas = {
  async carregar() {
    await this.popularFiltroProdutos();
    await this.carregarTabela();
    this.configurarEventos();
  },

  async popularFiltroProdutos() {
    try {
      const resp = await Api.get('/produtos');
      const selectFiltro = document.getElementById('filtro-venda-produto');
      const selectModal = document.getElementById('nova-venda-produto');

      const options = resp.produtos.map(p => `<option value="${p.id_produto}">${p.nome} (${p.categoria})</option>`).join('');

      if (selectFiltro) {
        selectFiltro.innerHTML = '<option value="">Todos os Produtos</option>' + options;
      }
      if (selectModal) {
        selectModal.innerHTML = options;
      }
    } catch (e) {
      console.error('Erro ao popular produtos em vendas:', e);
    }
  },

  async carregarTabela() {
    const idProd = document.getElementById('filtro-venda-produto')?.value || '';
    const dtInicio = document.getElementById('filtro-venda-inicio')?.value || '';
    const dtFim = document.getElementById('filtro-venda-fim')?.value || '';
    const promo = document.getElementById('filtro-venda-promocao')?.value || '';

    const tbody = document.getElementById('tabela-vendas-corpo');
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-slate-400">Carregando registros de vendas...</td></tr>`;

    try {
      const params = { limite: 100 };
      if (idProd) params.id_produto = idProd;
      if (dtInicio) params.data_inicio = dtInicio;
      if (dtFim) params.data_fim = dtFim;
      if (promo !== '') params.promocao = promo === '1';

      const vendas = await Api.get('/vendas', params);

      if (!vendas || vendas.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-slate-500">Nenhum registro de venda encontrado com os filtros selecionados.</td></tr>`;
        return;
      }

      tbody.innerHTML = '';
      vendas.forEach(v => {
        const partesData = v.data.split('-');
        const dataFmt = `${partesData[2]}/${partesData[1]}/${partesData[0]}`;

        const tr = document.createElement('tr');
        tr.className = 'border-b border-slate-100 hover:bg-slate-50 text-xs transition-colors';
        tr.innerHTML = `
          <td class="py-3 px-4 font-mono text-slate-400">#${v.id_venda}</td>
          <td class="py-3 px-4 font-semibold text-slate-900">${v.nome_produto}</td>
          <td class="py-3 px-4 text-slate-500">${v.categoria_produto}</td>
          <td class="py-3 px-4 text-slate-600">${dataFmt}</td>
          <td class="py-3 px-4 font-bold text-slate-800">${v.quantidade} un</td>
          <td class="py-3 px-4 font-semibold text-slate-700">R$ ${v.preco.toFixed(2)}</td>
          <td class="py-3 px-4">
            ${v.promocao ? '<span class="px-2 py-0.5 bg-amber-50 text-amber-800 border border-amber-200 rounded font-semibold text-[10px]">Promocional</span>' : '<span class="text-slate-500 text-[11px]">Regular</span>'}
          </td>
          <td class="py-3 px-4 text-right">
            <button onclick="window.Vendas.excluirVenda(${v.id_venda})" class="text-rose-700 hover:text-rose-900 bg-rose-50 hover:bg-rose-100 border border-rose-200 px-2 py-1 rounded text-xs transition-colors">
              Excluir
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-rose-700">Erro: ${err.message}</td></tr>`;
    }
  },

  configurarEventos() {
    const btnFiltro = document.getElementById('btn-filtrar-vendas');
    if (btnFiltro) {
      btnFiltro.addEventListener('click', () => this.carregarTabela());
    }

    const formVenda = document.getElementById('form-nova-venda');
    if (formVenda) {
      formVenda.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id_produto = parseInt(document.getElementById('nova-venda-produto').value, 10);
        const data = document.getElementById('nova-venda-data').value;
        const quantidade = parseInt(document.getElementById('nova-venda-quantidade').value, 10);
        const preco = parseFloat(document.getElementById('nova-venda-preco').value);
        const promocao = document.getElementById('nova-venda-promocao').checked;

        try {
          await Api.post('/vendas', { id_produto, data, quantidade, preco, promocao });
          window.Toast.mostrar('Venda registrada com sucesso. Estoque atualizado.');
          this.fecharModalNovaVenda();
          formVenda.reset();
          await this.carregarTabela();
          if (window.Dashboard) window.Dashboard.carregar();
          if (window.Produtos) window.Produtos.carregarTabela();
        } catch (err) {
          window.Toast.mostrar('Erro ao registrar venda: ' + err.message, 'erro');
        }
      });
    }

    const inputCsv = document.getElementById('input-upload-csv');
    if (inputCsv) {
      inputCsv.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('arquivo', file);

        try {
          window.Toast.mostrar('Processando e higienizando arquivo CSV...', 'info');
          const resp = await Api.upload('/vendas/upload-csv', formData);

          window.Toast.mostrar(
            `Importação finalizada. ${resp.linhas_inseridas} registros inseridos. (${resp.linhas_descartadas} descartados).`,
            'sucesso'
          );
          inputCsv.value = '';
          await this.carregarTabela();
          if (window.Dashboard) window.Dashboard.carregar();
          if (window.Produtos) window.Produtos.carregarTabela();
        } catch (err) {
          window.Toast.mostrar('Falha no processamento: ' + err.message, 'erro');
          inputCsv.value = '';
        }
      });
    }
  },

  abrirModalNovaVenda() {
    const inputData = document.getElementById('nova-venda-data');
    if (inputData && !inputData.value) {
      inputData.value = new Date().toISOString().split('T')[0];
    }
    document.getElementById('modal-nova-venda').classList.add('active');
  },

  fecharModalNovaVenda() {
    document.getElementById('modal-nova-venda').classList.remove('active');
  },

  baixarTemplateCSV() {
    window.location.href = '/api/vendas/template-csv';
  },

  async excluirVenda(idVenda) {
    if (!confirm('Deseja excluir este registro de venda?')) return;
    try {
      await Api.delete(`/vendas/${idVenda}`);
      window.Toast.mostrar('Registro de venda removido.');
      await this.carregarTabela();
      if (window.Dashboard) window.Dashboard.carregar();
    } catch (err) {
      window.Toast.mostrar('Erro ao remover: ' + err.message, 'erro');
    }
  }
};
