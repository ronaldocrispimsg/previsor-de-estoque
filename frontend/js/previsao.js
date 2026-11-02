/**
 * frontend/js/previsao.js
 * Módulo de Inteligência Preditiva e visualização gráfica de previsões.
 */

window.Previsao = {
  graficoInstancia: null,
  produtoSelecionadoId: null,

  async carregar() {
    await this.popularSeletorProdutos();
    this.configurarEventos();

    // Se já houver um produto selecionado, executa a previsão
    if (this.produtoSelecionadoId) {
      document.getElementById('previsao-select-produto').value = this.produtoSelecionadoId;
      await this.executarPrevisao();
    } else {
      // Seleciona o primeiro produto disponível
      const select = document.getElementById('previsao-select-produto');
      if (select && select.options.length > 0) {
        this.produtoSelecionadoId = parseInt(select.options[0].value, 10);
        await this.executarPrevisao();
      }
    }
  },

  async popularSeletorProdutos() {
    const resp = await Api.get('/produtos');
    const select = document.getElementById('previsao-select-produto');
    if (!select) return;

    select.innerHTML = resp.produtos.map(p => `
      <option value="${p.id_produto}">${p.nome} (${p.categoria}) - Est: ${p.estoque_atual} un</option>
    `).join('');
  },

  configurarEventos() {
    const select = document.getElementById('previsao-select-produto');
    const botoesHorizonte = document.querySelectorAll('.btn-horizonte');
    const checkPromo = document.getElementById('previsao-check-promocao');
    const btnGerar = document.getElementById('btn-gerar-previsao');

    if (select) {
      select.addEventListener('change', (e) => {
        this.produtoSelecionadoId = parseInt(e.target.value, 10);
        this.executarPrevisao();
      });
    }

    botoesHorizonte.forEach(btn => {
      btn.addEventListener('click', () => {
        botoesHorizonte.forEach(b => b.classList.remove('bg-emerald-600', 'text-white'));
        botoesHorizonte.forEach(b => b.classList.add('bg-slate-100', 'text-slate-700'));
        btn.classList.remove('bg-slate-100', 'text-slate-700');
        btn.classList.add('bg-emerald-600', 'text-white');
        this.executarPrevisao();
      });
    });

    if (checkPromo) {
      checkPromo.addEventListener('change', () => this.executarPrevisao());
    }

    if (btnGerar) {
      btnGerar.addEventListener('click', () => this.executarPrevisao(true));
    }
  },

  selecionarProdutoEPrever(idProduto) {
    this.produtoSelecionadoId = idProduto;
    window.Navegacao.irParaAba('previsao');
  },

  getHorizonteSelecionado() {
    const btnAtivo = document.querySelector('.btn-horizonte.bg-emerald-600');
    return btnAtivo ? parseInt(btnAtivo.dataset.dias, 10) : 15;
  },

  async executarPrevisao(salvarNoBanco = false) {
    const select = document.getElementById('previsao-select-produto');
    if (!select || !select.value) return;

    const idProduto = parseInt(select.value, 10);
    const horizonteDias = this.getHorizonteSelecionado();
    const considerarPromocao = document.getElementById('previsao-check-promocao')?.checked || false;

    const loadingEl = document.getElementById('previsao-loading');
    if (loadingEl) loadingEl.classList.remove('hidden');

    try {
      let dados;
      if (salvarNoBanco) {
        dados = await Api.post('/previsoes/gerar', {
          id_produto: idProduto,
          horizonte_dias: horizonteDias,
          considerar_promocao: considerarPromocao
        });
        alert('Previsão gerada e salva no histórico do banco com sucesso!');
      } else {
        dados = await Api.get(`/previsoes/${idProduto}`, {
          horizonte_dias: horizonteDias,
          considerar_promocao: considerarPromocao
        });
      }

      this.renderizarResultados(dados);
    } catch (err) {
      alert('Erro ao calcular previsão: ' + err.message);
    } finally {
      if (loadingEl) loadingEl.classList.add('hidden');
    }
  },

  renderizarResultados(dados) {
    const r = dados.resumo;
    const m = dados.metricas;

    document.getElementById('prev-resumo-produto').textContent = r.nome_produto;
    document.getElementById('prev-resumo-periodo').textContent = r.periodo;
    document.getElementById('prev-resumo-demanda').textContent = `${r.demanda_prevista} un`;
    document.getElementById('prev-resumo-estoque').textContent = `${r.estoque_atual} un`;
    document.getElementById('prev-resumo-sugestao').textContent = `${r.sugestao_reposicao} un`;

    const elRisco = document.getElementById('prev-resumo-risco');
    if (r.status_risco === 'RUPTURA') {
      elRisco.className = 'badge-ruptura';
      elRisco.textContent = 'Risco de Ruptura';
    } else if (r.status_risco === 'EXCESSO') {
      elRisco.className = 'badge-excesso';
      elRisco.textContent = 'Risco de Excesso';
    } else {
      elRisco.className = 'badge-equilibrado';
      elRisco.textContent = 'Estoque Equilibrado';
    }

    document.getElementById('prev-resumo-sazonalidade').textContent = r.impacto_sazonal_identificado ?
      `${r.impacto_sazonal_identificado} (x${r.multiplicador_sazonal})` : 'Padrão Regular (x1.0)';

    document.getElementById('prev-metric-acuracia').textContent = `${m.acuracia_estimada}%`;
    document.getElementById('prev-metric-mae').textContent = `${m.mae} un`;
    document.getElementById('prev-metric-rmse').textContent = `${m.rmse} un`;
    document.getElementById('prev-metric-mape').textContent = `${m.mape}%`;

    this.renderizarGrafico(dados.serie_temporal);
  },

  renderizarGrafico(serieTemporal) {
    const ctx = document.getElementById('chart-previsao-detalhado').getContext('2d');

    const labels = serieTemporal.map(p => {
      const partes = p.data.split('-');
      return `${partes[2]}/${partes[1]}`;
    });

    const realData = serieTemporal.map(p => p.quantidade_historica);
    const previstoData = serieTemporal.map(p => p.demanda_prevista);
    const infData = serieTemporal.map(p => p.limite_inferior);
    const supData = serieTemporal.map(p => p.limite_superior);

    if (this.graficoInstancia) {
      this.graficoInstancia.destroy();
    }

    this.graficoInstancia = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Vendas Reais Observadas',
            data: realData,
            borderColor: '#059669',
            backgroundColor: 'rgba(5, 150, 105, 0.15)',
            borderWidth: 2,
            pointRadius: 3,
            tension: 0.3
          },
          {
            label: 'Demanda Prevista (Predikta)',
            data: previstoData,
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37, 99, 235, 0.12)',
            borderWidth: 2.5,
            borderDash: [5, 5],
            pointRadius: 4,
            pointBackgroundColor: '#2563eb',
            tension: 0.3
          },
          {
            label: 'Intervalo Superior (95%)',
            data: supData,
            borderColor: 'rgba(148, 163, 184, 0.4)',
            borderWidth: 1,
            borderDash: [2, 2],
            pointRadius: 0,
            fill: false
          },
          {
            label: 'Intervalo Inferior (95%)',
            data: infData,
            borderColor: 'rgba(148, 163, 184, 0.4)',
            borderWidth: 1,
            borderDash: [2, 2],
            pointRadius: 0,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { font: { family: 'Inter', size: 11 } } },
          tooltip: { cornerRadius: 8, padding: 10 }
        },
        scales: {
          y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
          x: { grid: { display: false } }
        }
      }
    });
  }
};
