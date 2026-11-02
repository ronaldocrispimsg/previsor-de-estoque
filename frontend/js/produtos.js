/**
 * frontend/js/produtos.js
 * Gerenciamento do catálogo de produtos de supermercado.
 */

window.Produtos = {
  categoriasCache: [],
  produtoEmEdicaoId: null,

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
      const selectEditModal = document.getElementById('edit-prod-categoria');

      const options = this.categoriasCache.map(c => `<option value="${c}">${c}</option>`).join('');

      if (selectFiltro) {
        selectFiltro.innerHTML = '<option value="">Todas as Categorias</option>' + options;
      }
      if (selectModal) {
        selectModal.innerHTML = options + '<option value="Outros">Outros</option>';
      }
      if (selectEditModal) {
        selectEditModal.innerHTML = options;
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
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-slate-400">Carregando catálogo...</td></tr>`;

    try {
      const resp = await Api.get('/produtos', {
        categoria,
        busca,
        status_filtro: statusFiltro
      });

      if (!resp.produtos || resp.produtos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-slate-500">Nenhum produto encontrado com os filtros aplicados.</td></tr>`;
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
            <div class="flex items-center gap-1.5">
              <span class="font-bold ${p.estoque_atual < p.estoque_minimo ? 'text-red-600' : 'text-slate-800'}">${p.estoque_atual} un</span>
              <button onclick="window.Produtos.ajustarEstoqueRapido(${p.id_produto}, 20)" class="text-[10px] bg-slate-100 hover:bg-slate-200 text-slate-600 px-1.5 py-0.5 rounded font-bold" title="Adicionar +20">+20</button>
            </div>
          </td>
          <td class="py-3 px-4 text-slate-500">
            <span title="Ponto de Pedido: ${p.ponto_de_pedido || '--'} un">${p.estoque_minimo} un</span>
            <span class="block text-[10px] text-slate-400">Ponto: ${p.ponto_de_pedido ? p.ponto_de_pedido + ' un' : '--'}</span>
          </td>
          <td class="py-3 px-4 text-slate-500 text-xs">${p.lead_time_dias} dias</td>
          <td class="py-3 px-4"><span class="${badgeCls}">${badgeLabel}</span></td>
          <td class="py-3 px-4 text-right space-x-2">
            <button onclick="window.Previsao.selecionarProdutoEPrever(${p.id_produto})" class="text-xs bg-emerald-50 text-emerald-700 hover:bg-emerald-100 px-2.5 py-1.5 rounded font-medium transition-colors">
              Prever Demanda
            </button>
            <button onclick="window.Produtos.abrirModalEdicao(${JSON.stringify(p).replace(/"/g, '&quot;')})" class="text-xs text-blue-600 hover:text-blue-800 p-1" title="Editar Parâmetros">
              ✏️
            </button>
            <button onclick="window.Produtos.excluirProduto(${p.id_produto}, '${p.nome}')" class="text-xs text-red-500 hover:text-red-700 p-1" title="Excluir">
              🗑️
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-red-500">Erro ao carregar produtos: ${err.message}</td></tr>`;
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
          window.Toast.mostrar(`Produto "${nome}" cadastrado com sucesso!`);
          this.fecharModalNovo();
          formNovo.reset();
          await this.carregar();
          if (window.Dashboard) window.Dashboard.carregar();
        } catch (err) {
          window.Toast.mostrar('Erro ao criar produto: ' + err.message, 'erro');
        }
      });
    }

    const formEdit = document.getElementById('form-editar-produto');
    if (formEdit) {
      formEdit.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!this.produtoEmEdicaoId) return;

        const nome = document.getElementById('edit-prod-nome').value;
        const categoria = document.getElementById('edit-prod-categoria').value;
        const preco_base = parseFloat(document.getElementById('edit-prod-preco').value);
        const estoque_atual = parseInt(document.getElementById('edit-prod-estoque').value, 10);
        const estoque_minimo = parseInt(document.getElementById('edit-prod-estoque-min').value, 10);
        const lead_time_dias = parseInt(document.getElementById('edit-prod-leadtime').value, 10);

        try {
          await Api.put(`/produtos/${this.produtoEmEdicaoId}`, {
            nome,
            categoria,
            preco_base,
            estoque_atual,
            estoque_minimo,
            lead_time_dias
          });
          window.Toast.mostrar(`Produto atualizado com sucesso!`);
          this.fecharModalEdicao();
          await this.carregar();
          if (window.Dashboard) window.Dashboard.carregar();
        } catch (err) {
          window.Toast.mostrar('Erro ao atualizar produto: ' + err.message, 'erro');
        }
      });
    }
  },

  async ajustarEstoqueRapido(idProduto, quantidade) {
    try {
      const resp = await Api.post(`/produtos/${idProduto}/ajuste-estoque`, {
        quantidade,
        motivo: "Entrada Rápida"
      });
      window.Toast.mostrar(`Estoque ajustado! Novo saldo: ${resp.estoque_atual} un.`);
      await this.carregarTabela();
      if (window.Dashboard) window.Dashboard.carregar();
    } catch (err) {
      window.Toast.mostrar('Erro ao ajustar estoque: ' + err.message, 'erro');
    }
  },

  abrirModalNovo() {
    document.getElementById('modal-novo-produto').classList.add('active');
  },

  fecharModalNovo() {
    document.getElementById('modal-novo-produto').classList.remove('active');
  },

  abrirModalEdicao(produto) {
    this.produtoEmEdicaoId = produto.id_produto;
    document.getElementById('edit-prod-nome').value = produto.nome;
    document.getElementById('edit-prod-categoria').value = produto.categoria;
    document.getElementById('edit-prod-preco').value = produto.preco_base;
    document.getElementById('edit-prod-estoque').value = produto.estoque_atual;
    document.getElementById('edit-prod-estoque-min').value = produto.estoque_minimo;
    document.getElementById('edit-prod-leadtime').value = produto.lead_time_dias;
    document.getElementById('modal-editar-produto').classList.add('active');
  },

  fecharModalEdicao() {
    document.getElementById('modal-editar-produto').classList.remove('active');
    this.produtoEmEdicaoId = null;
  },

  async excluirProduto(id, nome) {
    if (!confirm(`Deseja realmente excluir o produto "${nome}"? O histórico de vendas associado também será removido.`)) {
      return;
    }
    try {
      await Api.delete(`/produtos/${id}`);
      window.Toast.mostrar(`Produto "${nome}" removido.`);
      await this.carregar();
      if (window.Dashboard) window.Dashboard.carregar();
    } catch (err) {
      window.Toast.mostrar('Erro ao excluir: ' + err.message, 'erro');
    }
  }
};
