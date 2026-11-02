/**
 * frontend/js/produtos.js
 * Gerenciamento do catálogo de produtos de supermercado.
 */

window.Produtos = {
  categoriasCache: [],

  async carregar() {
    await this.carregarCategorias();
    await this.carregarTabela();
    this.configurarEventos();
  },

  async carregarCategorias() {
    try {
      this.categoriasCache = await Api.get('/produtos/categorias');
      const selectFiltro = document.getElementById('filtro-produto-categoria');
      const selectModal = document.getElementById('novo-prod-categoria');

      const options = this.categoriasCache.map(c => `<option value="${c}">${c}</option>`).join('');

      if (selectFiltro) {
        selectFiltro.innerHTML = '<option value="">Todas as Categorias</option>' + options;
      }
      if (selectModal) {
        selectModal.innerHTML = options + '<option value="Outros">Outros</option>';
      }
    } catch (err) {
      console.error('Erro ao carregar categorias:', err);
    }
  },

  async carregarTabela() {
    const categoria = document.getElementById('filtro-produto-categoria')?.value || '';
    const busca = document.getElementById('filtro-produto-busca')?.value || '';
    const statusFiltro = document.getElementById('filtro-produto-status')?.value || '';

    const tbody = document.getElementById('tabela-produtos-corpo');
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-slate-400">Carregando catálogo...</td></tr>`;

    try {
      const resp = await Api.get('/produtos', {
        categoria,
        busca,
        status_filtro: statusFiltro
      });

      if (!resp.produtos || resp.produtos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-slate-500">Nenhum produto encontrado com os filtros aplicados.</td></tr>`;
        return;
      }

      tbody.innerHTML = '';
      resp.produtos.forEach(p => {
        let badgeCls = 'badge-equilibrado';
        let badgeLabel = 'Equilibrado';

        if (p.status_estoque === 'RUPTURA') {
          badgeCls = 'badge-ruptura';
          badgeLabel = 'Ruptura';
        } else if (p.status_estoque === 'ATENCAO') {
          badgeCls = 'badge-atencao';
          badgeLabel = 'Atenção';
        } else if (p.status_estoque === 'EXCESSO') {
          badgeCls = 'badge-excesso';
          badgeLabel = 'Excesso';
        }

        const tr = document.createElement('tr');
        tr.className = 'border-b border-slate-100 hover:bg-slate-50 transition-colors text-sm';
        tr.innerHTML = `
          <td class="py-3 px-4 font-medium text-slate-900">${p.nome}</td>
          <td class="py-3 px-4 text-slate-600"><span class="bg-slate-100 text-slate-700 px-2.5 py-1 rounded text-xs">${p.categoria}</span></td>
          <td class="py-3 px-4 text-slate-800 font-semibold">R$ ${p.preco_base.toFixed(2)}</td>
          <td class="py-3 px-4">
            <span class="font-bold ${p.estoque_atual < p.estoque_minimo ? 'text-red-600' : 'text-slate-800'}">${p.estoque_atual} un</span>
          </td>
          <td class="py-3 px-4 text-slate-500">${p.estoque_minimo} un</td>
          <td class="py-3 px-4"><span class="${badgeCls}">${badgeLabel}</span></td>
          <td class="py-3 px-4 text-right space-x-2">
            <button onclick="window.Previsao.selecionarProdutoEPrever(${p.id_produto})" class="text-xs bg-emerald-50 text-emerald-700 hover:bg-emerald-100 px-2.5 py-1.5 rounded font-medium transition-colors">
              Prever Demanda
            </button>
            <button onclick="window.Produtos.excluirProduto(${p.id_produto}, '${p.nome}')" class="text-xs text-red-500 hover:text-red-700 p-1">
              🗑️
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-red-500">Erro ao carregar produtos: ${err.message}</td></tr>`;
    }
  },

  configurarEventos() {
    const buscaInput = document.getElementById('filtro-produto-busca');
    const categoriaSelect = document.getElementById('filtro-produto-categoria');
    const statusSelect = document.getElementById('filtro-produto-status');

    if (buscaInput) {
      buscaInput.addEventListener('input', () => this.carregarTabela());
    }
    if (categoriaSelect) {
      categoriaSelect.addEventListener('change', () => this.carregarTabela());
    }
    if (statusSelect) {
      statusSelect.addEventListener('change', () => this.carregarTabela());
    }

    const formNovo = document.getElementById('form-novo-produto');
    if (formNovo) {
      formNovo.addEventListener('submit', async (e) => {
        e.preventDefault();
        const nome = document.getElementById('novo-prod-nome').value;
        const categoria = document.getElementById('novo-prod-categoria').value;
        const preco_base = parseFloat(document.getElementById('novo-prod-preco').value);
        const estoque_atual = parseInt(document.getElementById('novo-prod-estoque').value, 10);
        const estoque_minimo = parseInt(document.getElementById('novo-prod-estoque-min').value, 10);
        const lead_time_dias = parseInt(document.getElementById('novo-prod-leadtime').value, 10);

        try {
          await Api.post('/produtos', {
            nome,
            categoria,
            preco_base,
            estoque_atual,
            estoque_minimo,
            lead_time_dias
          });
          this.fecharModalNovo();
          formNovo.reset();
          await this.carregar();
          if (window.Dashboard) window.Dashboard.carregar();
        } catch (err) {
          alert('Erro ao criar produto: ' + err.message);
        }
      });
    }
  },

  abrirModalNovo() {
    document.getElementById('modal-novo-produto').classList.add('active');
  },

  fecharModalNovo() {
    document.getElementById('modal-novo-produto').classList.remove('active');
  },

  async excluirProduto(id, nome) {
    if (!confirm(`Deseja realmente excluir o produto "${nome}"? O histórico de vendas associado também será removido.`)) {
      return;
    }
    try {
      await Api.delete(`/produtos/${id}`);
      await this.carregar();
      if (window.Dashboard) window.Dashboard.carregar();
    } catch (err) {
      alert('Erro ao excluir: ' + err.message);
    }
  }
};
