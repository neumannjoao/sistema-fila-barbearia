/*
Sistema de Fila Digital para Barbearia
Arquivo JavaScript Principal

Este arquivo contém toda a lógica de frontend do sistema,
incluindo comunicação com a API, manipulação da interface
e funcionalidades em tempo real.

ATENÇÃO: Este código é propriedade intelectual protegida.
Uso não autorizado é proibido por lei.
*/

// ===== CONFIGURAÇÕES GLOBAIS =====
const CONFIG = {
    API_BASE_URL: '/api',
    REFRESH_INTERVAL: 5000, // 5 segundos
    TOAST_DURATION: 5000,   // 5 segundos
    MAX_RETRIES: 3
};

// ===== ESTADO GLOBAL DA APLICAÇÃO =====
let appState = {
    currentSection: 'home',
    barbeiros: [],
    filaCompleta: {},
    autoRefresh: true,
    refreshInterval: null,
    isLoading: false
};

// ===== INICIALIZAÇÃO DA APLICAÇÃO =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando Sistema de Fila Digital para Barbearia');
    
    // Inicializa componentes
    inicializarNavegacao();
    inicializarFormularios();
    inicializarEventListeners();
    
    // Carrega dados iniciais
    carregarDadosIniciais();
    
    // Inicia auto-refresh
    iniciarAutoRefresh();
    
    console.log('✅ Sistema inicializado com sucesso');
});

// ===== NAVEGAÇÃO =====
function inicializarNavegacao() {
    /**
     * Configura a navegação entre seções da aplicação.
     * Implementa um sistema SPA (Single Page Application) simples.
     */
    
    // Event listeners para links de navegação
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetSection = this.getAttribute('href').substring(1);
            navegarPara(targetSection);
        });
    });
    
    // Navegação inicial baseada na URL
    const hash = window.location.hash.substring(1);
    if (hash && ['home', 'cadastro', 'fila', 'barbeiros', 'relatorios'].includes(hash)) {
        navegarPara(hash);
    } else {
        navegarPara('home');
    }
}

function navegarPara(secao) {
    /**
     * Navega para uma seção específica da aplicação.
     * 
     * @param {string} secao - Nome da seção de destino
     */
    
    // Atualiza estado
    appState.currentSection = secao;
    
    // Oculta todas as seções
    document.querySelectorAll('.section-content').forEach(section => {
        section.classList.add('d-none');
    });
    
    // Mostra seção alvo
    const targetSection = document.getElementById(secao);
    if (targetSection) {
        targetSection.classList.remove('d-none');
        targetSection.classList.add('fade-in');
    }
    
    // Atualiza navegação ativa
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    const activeLink = document.querySelector(`[href="#${secao}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
    
    // Atualiza URL
    window.location.hash = secao;
    
    // Carrega dados específicos da seção
    carregarDadosSecao(secao);
    
    console.log(`📍 Navegando para: ${secao}`);
}

function carregarDadosSecao(secao) {
    /**
     * Carrega dados específicos para cada seção.
     * 
     * @param {string} secao - Nome da seção
     */
    
    switch (secao) {
        case 'home':
            carregarStatusSistema();
            break;
        case 'cadastro':
            carregarBarbeiros();
            break;
        case 'fila':
            carregarFilaCompleta();
            break;
        case 'barbeiros':
            carregarListaBarbeiros();
            break;
        case 'relatorios':
            carregarEstatisticas();
            break;
    }
}

// ===== FORMULÁRIOS =====
function inicializarFormularios() {
    /**
     * Configura todos os formulários da aplicação.
     */
    
    // Formulário de cadastro de cliente
    const formCadastro = document.getElementById('form-cadastro');
    if (formCadastro) {
        formCadastro.addEventListener('submit', function(e) {
            e.preventDefault();
            cadastrarCliente();
        });
    }
    
    // Formulário de novo barbeiro
    const formNovoBarbeiro = document.getElementById('form-novo-barbeiro');
    if (formNovoBarbeiro) {
        formNovoBarbeiro.addEventListener('submit', function(e) {
            e.preventDefault();
            criarBarbeiro();
        });
    }
}

function inicializarEventListeners() {
    /**
     * Configura event listeners globais da aplicação.
     */
    
    // Auto-refresh toggle
    const autoRefreshToggle = document.getElementById('auto-refresh');
    if (autoRefreshToggle) {
        autoRefreshToggle.addEventListener('change', function() {
            appState.autoRefresh = this.checked;
            if (this.checked) {
                iniciarAutoRefresh();
            } else {
                pararAutoRefresh();
            }
        });
    }
    
    // Teclas de atalho
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + R para atualizar
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            atualizarDados();
        }
        
        // Escape para fechar modais
        if (e.key === 'Escape') {
            fecharModais();
        }
    });
}

// ===== API CALLS =====
async function apiCall(endpoint, options = {}) {
    /**
     * Função utilitária para chamadas à API com tratamento de erros.
     * 
     * @param {string} endpoint - Endpoint da API
     * @param {Object} options - Opções da requisição
     * @returns {Promise} Resposta da API
     */
    
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        mostrarLoading();
        
        const response = await fetch(url, finalOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.erro || `Erro HTTP: ${response.status}`);
        }
        
        return data;
        
    } catch (error) {
        console.error(`❌ Erro na API (${endpoint}):`, error);
        mostrarToast('Erro', error.message, 'danger');
        throw error;
        
    } finally {
        ocultarLoading();
    }
}

// ===== CARREGAMENTO DE DADOS =====
async function carregarDadosIniciais() {
    /**
     * Carrega dados iniciais necessários para a aplicação.
     */
    
    try {
        await Promise.all([
            carregarBarbeiros(),
            carregarStatusSistema()
        ]);
        
        console.log('✅ Dados iniciais carregados');
        
    } catch (error) {
        console.error('❌ Erro ao carregar dados iniciais:', error);
        mostrarToast('Erro', 'Falha ao carregar dados iniciais', 'danger');
    }
}

async function carregarBarbeiros() {
    /**
     * Carrega a lista de barbeiros do sistema.
     */
    
    try {
        const response = await apiCall('/barbeiros');
        appState.barbeiros = response.barbeiros || [];
        
        // Atualiza select de barbeiros no formulário
        atualizarSelectBarbeiros();
        
        console.log(`📋 ${appState.barbeiros.length} barbeiros carregados`);
        
    } catch (error) {
        console.error('❌ Erro ao carregar barbeiros:', error);
    }
}

async function carregarStatusSistema() {
    /**
     * Carrega o status atual do sistema.
     */
    
    try {
        const response = await apiCall('/status');
        renderizarStatusCards(response);
        
        console.log('📊 Status do sistema atualizado');
        
    } catch (error) {
        console.error('❌ Erro ao carregar status:', error);
    }
}

async function carregarFilaCompleta() {
    /**
     * Carrega a fila completa de todos os barbeiros.
     */
    
    try {
        const response = await apiCall('/fila');
        appState.filaCompleta = response.fila_completa || {};
        
        renderizarFilaCompleta();
        
        console.log('👥 Fila completa atualizada');
        
    } catch (error) {
        console.error('❌ Erro ao carregar fila:', error);
    }
}

async function carregarListaBarbeiros() {
    /**
     * Carrega e renderiza a lista de barbeiros para gerenciamento.
     */
    
    try {
        await carregarBarbeiros();
        renderizarListaBarbeiros();
        
    } catch (error) {
        console.error('❌ Erro ao carregar lista de barbeiros:', error);
    }
}

async function carregarEstatisticas() {
    /**
     * Carrega estatísticas e relatórios do sistema.
     */
    
    try {
        const response = await apiCall('/relatorios/estatisticas?periodo=hoje');
        renderizarEstatisticas(response.estatisticas);
        
        console.log('📈 Estatísticas carregadas');
        
    } catch (error) {
        console.error('❌ Erro ao carregar estatísticas:', error);
    }
}

// ===== RENDERIZAÇÃO =====
function renderizarStatusCards(statusData) {
    /**
     * Renderiza os cards de status do sistema.
     * 
     * @param {Object} statusData - Dados do status do sistema
     */
    
    const container = document.getElementById('status-cards');
    if (!container) return;
    
    const stats = statusData.estatisticas || {};
    
    const cards = [
        {
            icon: 'fas fa-user-tie',
            number: stats.barbeiros_ativos || 0,
            label: 'Barbeiros Ativos',
            color: 'primary'
        },
        {
            icon: 'fas fa-clock',
            number: stats.clientes_aguardando || 0,
            label: 'Clientes Aguardando',
            color: 'warning'
        },
        {
            icon: 'fas fa-cut',
            number: stats.clientes_atendendo || 0,
            label: 'Em Atendimento',
            color: 'success'
        },
        {
            icon: 'fas fa-chart-line',
            number: stats.total_barbeiros || 0,
            label: 'Total de Barbeiros',
            color: 'info'
        }
    ];
    
    container.innerHTML = cards.map(card => `
        <div class="col-lg-3 col-md-6">
            <div class="status-card bg-gradient-${card.color}">
                <div class="status-icon">
                    <i class="${card.icon}"></i>
                </div>
                <div class="status-number">${card.number}</div>
                <div class="status-label">${card.label}</div>
            </div>
        </div>
    `).join('');
}

function renderizarFilaCompleta() {
    /**
     * Renderiza a fila completa de todos os barbeiros.
     */
    
    const container = document.getElementById('fila-barbeiros');
    if (!container) return;
    
    const filas = Object.values(appState.filaCompleta);
    
    if (filas.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="empty-state">
                    <i class="fas fa-users"></i>
                    <h4>Nenhuma fila encontrada</h4>
                    <p>Não há barbeiros ativos no momento.</p>
                </div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = filas.map(fila => {
        const barbeiro = fila.barbeiro;
        const filaAguardando = fila.fila_aguardando || [];
        const clienteAtendendo = fila.cliente_atendendo;
        
        return `
            <div class="col-lg-4 col-md-6">
                <div class="fila-card">
                    <div class="fila-header">
                        <h4>
                            <i class="fas fa-user-tie me-2"></i>
                            ${barbeiro.nome}
                        </h4>
                        <small>
                            ${filaAguardando.length} cliente(s) aguardando
                        </small>
                    </div>
                    <div class="fila-body">
                        ${clienteAtendendo ? `
                            <div class="cliente-item cliente-atendendo">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <div class="cliente-ficha">Ficha ${clienteAtendendo.numero_ficha}</div>
                                        <div class="cliente-nome">${clienteAtendendo.nome}</div>
                                        <div class="cliente-posicao">
                                            <i class="fas fa-cut me-1"></i>
                                            Em atendimento
                                        </div>
                                    </div>
                                    <button class="btn btn-sm btn-success" 
                                            onclick="concluirAtendimento(${clienteAtendendo.id})">
                                        <i class="fas fa-check"></i>
                                    </button>
                                </div>
                            </div>
                        ` : ''}
                        
                        ${filaAguardando.length > 0 ? filaAguardando.map(cliente => `
                            <div class="cliente-item">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <div class="cliente-ficha">Ficha ${cliente.numero_ficha}</div>
                                        <div class="cliente-nome">${cliente.nome}</div>
                                        <div class="cliente-posicao">
                                            <i class="fas fa-clock me-1"></i>
                                            ${cliente.posicao_fila}º na fila
                                        </div>
                                    </div>
                                    <div class="btn-group">
                                        ${cliente.posicao_fila === 1 && !clienteAtendendo ? `
                                            <button class="btn btn-sm btn-primary" 
                                                    onclick="chamarProximoCliente(${barbeiro.id})">
                                                <i class="fas fa-play"></i>
                                            </button>
                                        ` : ''}
                                        <button class="btn btn-sm btn-outline-danger" 
                                                onclick="cancelarCliente(${cliente.id})">
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `).join('') : `
                            <div class="empty-state">
                                <i class="fas fa-clock"></i>
                                <p>Nenhum cliente aguardando</p>
                            </div>
                        `}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function renderizarListaBarbeiros() {
    /**
     * Renderiza a lista de barbeiros para gerenciamento.
     */
    
    const container = document.getElementById('lista-barbeiros');
    if (!container) return;
    
    if (appState.barbeiros.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="empty-state">
                    <i class="fas fa-user-tie"></i>
                    <h4>Nenhum barbeiro cadastrado</h4>
                    <p>Clique em "Novo Barbeiro" para começar.</p>
                </div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = appState.barbeiros.map(barbeiro => `
        <div class="col-lg-4 col-md-6">
            <div class="barbeiro-card">
                <div class="card-body text-center">
                    <div class="barbeiro-status ${barbeiro.ativo ? '' : 'inativo'}"></div>
                    <div class="barbeiro-avatar">
                        <i class="fas fa-user-tie"></i>
                    </div>
                    <h5 class="card-title">${barbeiro.nome}</h5>
                    <p class="card-text">
                        <span class="badge ${barbeiro.ativo ? 'bg-success' : 'bg-secondary'}">
                            ${barbeiro.ativo ? 'Ativo' : 'Inativo'}
                        </span>
                    </p>
                    <div class="btn-group w-100">
                        <button class="btn ${barbeiro.ativo ? 'btn-warning' : 'btn-success'}" 
                                onclick="alternarStatusBarbeiro(${barbeiro.id}, ${!barbeiro.ativo})">
                            <i class="fas ${barbeiro.ativo ? 'fa-pause' : 'fa-play'}"></i>
                            ${barbeiro.ativo ? 'Desativar' : 'Ativar'}
                        </button>
                        <button class="btn btn-primary" 
                                onclick="verFilaBarbeiro(${barbeiro.id})">
                            <i class="fas fa-users"></i>
                            Ver Fila
                        </button>
                        <button class="btn btn-danger" 
                                onclick="removerBarbeiro(${barbeiro.id})">
                            <i class="fas fa-trash"></i>
                            Remover
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function renderizarEstatisticas(estatisticas) {
    /**
     * Renderiza as estatísticas do sistema.
     * 
     * @param {Object} estatisticas - Dados das estatísticas
     */
    
    const container = document.getElementById('estatisticas-dia');
    if (!container) return;
    
    container.innerHTML = `
        <div class="row g-3">
            <div class="col-6">
                <div class="text-center">
                    <h4 class="text-primary">${estatisticas.total_atendimentos || 0}</h4>
                    <small class="text-muted">Atendimentos Hoje</small>
                </div>
            </div>
            <div class="col-6">
                <div class="text-center">
                    <h4 class="text-success">${estatisticas.tempo_medio_espera || 0} min</h4>
                    <small class="text-muted">Tempo Médio de Espera</small>
                </div>
            </div>
            <div class="col-6">
                <div class="text-center">
                    <h4 class="text-info">${estatisticas.tempo_medio_atendimento || 0} min</h4>
                    <small class="text-muted">Tempo Médio de Atendimento</small>
                </div>
            </div>
            <div class="col-6">
                <div class="text-center">
                    <h4 class="text-warning">${estatisticas.tempo_total_medio || 0} min</h4>
                    <small class="text-muted">Tempo Total Médio</small>
                </div>
            </div>
        </div>
    `;
}

function atualizarSelectBarbeiros() {
    /**
     * Atualiza o select de barbeiros no formulário de cadastro.
     */
    
    const select = document.getElementById('barbeiro-preferido');
    if (!select) return;
    
    // Limpa opções existentes (exceto a primeira)
    select.innerHTML = '<option value="">Selecione um barbeiro...</option>';
    
    // Adiciona barbeiros ativos
    const barbeirosAtivos = appState.barbeiros.filter(b => b.ativo);
    
    barbeirosAtivos.forEach(barbeiro => {
        const option = document.createElement('option');
        option.value = barbeiro.id;
        option.textContent = barbeiro.nome;
        select.appendChild(option);
    });
    
    if (barbeirosAtivos.length === 0) {
        select.innerHTML = '<option value="">Nenhum barbeiro ativo</option>';
        select.disabled = true;
    } else {
        select.disabled = false;
    }
}

// ===== AÇÕES DO USUÁRIO =====
async function cadastrarCliente() {
    /**
     * Cadastra um novo cliente na fila.
     */
    
    const form = document.getElementById('form-cadastro');
    const formData = new FormData(form);
    
    const dados = {
        nome: document.getElementById('nome-cliente').value.trim(),
        numero_ficha: parseInt(document.getElementById('numero-ficha').value),
        barbeiro_id: parseInt(document.getElementById('barbeiro-preferido').value)
    };
    
    // Validações
    if (!dados.nome || dados.nome.length < 2) {
        mostrarToast('Erro', 'Nome deve ter pelo menos 2 caracteres', 'danger');
        return;
    }
    
    if (!dados.numero_ficha || dados.numero_ficha <= 0) {
        mostrarToast('Erro', 'Número da ficha deve ser válido', 'danger');
        return;
    }
    
    if (!dados.barbeiro_id) {
        mostrarToast('Erro', 'Selecione um barbeiro', 'danger');
        return;
    }
    
    try {
        const response = await apiCall('/clientes', {
            method: 'POST',
            body: JSON.stringify(dados)
        });
        
        mostrarToast('Sucesso', response.mensagem, 'success');
        limparFormulario();
        
        // Atualiza dados se estiver na seção de fila
        if (appState.currentSection === 'fila') {
            carregarFilaCompleta();
        }
        
    } catch (error) {
        console.error('❌ Erro ao cadastrar cliente:', error);
    }
}

async function criarBarbeiro() {
    /**
     * Cria um novo barbeiro no sistema.
     */
    
    const nome = document.getElementById('nome-barbeiro').value.trim();
    
    if (!nome || nome.length < 2) {
        mostrarToast('Erro', 'Nome deve ter pelo menos 2 caracteres', 'danger');
        return;
    }
    
    try {
        const response = await apiCall('/barbeiros', {
            method: 'POST',
            body: JSON.stringify({ nome })
        });
        
        mostrarToast('Sucesso', response.mensagem, 'success');
        
        // Fecha modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('modal-novo-barbeiro'));
        modal.hide();
        
        // Limpa formulário
        document.getElementById('nome-barbeiro').value = '';
        
        // Atualiza dados
        await carregarBarbeiros();
        if (appState.currentSection === 'barbeiros') {
            renderizarListaBarbeiros();
        }
        
    } catch (error) {
        console.error('❌ Erro ao criar barbeiro:', error);
    }
}

async function chamarProximoCliente(barbeiroId) {
    /**
     * Chama o próximo cliente da fila de um barbeiro.
     * 
     * @param {number} barbeiroId - ID do barbeiro
     */
    
    try {
        const response = await apiCall(`/barbeiros/${barbeiroId}/proximo`, {
            method: 'POST'
        });
        
        if (response.cliente_chamado) {
            mostrarToast('Cliente Chamado', response.mensagem, 'success');
            carregarFilaCompleta();
        } else {
            mostrarToast('Info', response.mensagem, 'info');
        }
        
    } catch (error) {
        console.error('❌ Erro ao chamar próximo cliente:', error);
    }
}

async function concluirAtendimento(clienteId) {
    /**
     * Conclui o atendimento de um cliente.
     * 
     * @param {number} clienteId - ID do cliente
     */
    
    try {
        const response = await apiCall(`/clientes/${clienteId}/concluir`, {
            method: 'PUT'
        });
        
        mostrarToast('Atendimento Concluído', response.mensagem, 'success');
        carregarFilaCompleta();
        
    } catch (error) {
        console.error('❌ Erro ao concluir atendimento:', error);
    }
}

async function cancelarCliente(clienteId) {
    /**
     * Cancela o atendimento de um cliente.
     * 
     * @param {number} clienteId - ID do cliente
     */
    
    if (!confirm('Tem certeza que deseja cancelar este atendimento?')) {
        return;
    }
    
    try {
        const response = await apiCall(`/clientes/${clienteId}/cancelar`, {
            method: 'PUT'
        });
        
        mostrarToast('Atendimento Cancelado', response.mensagem, 'warning');
        carregarFilaCompleta();
        
    } catch (error) {
        console.error('❌ Erro ao cancelar cliente:', error);
    }
}

async function alternarStatusBarbeiro(barbeiroId, ativar) {
    /**
     * Ativa ou desativa um barbeiro.
     * 
     * @param {number} barbeiroId - ID do barbeiro
     * @param {boolean} ativar - Se deve ativar ou desativar
     */
    
    const endpoint = ativar ? 'ativar' : 'desativar';
    
    try {
        const response = await apiCall(`/barbeiros/${barbeiroId}/${endpoint}`, {
            method: 'PUT'
        });
        
        mostrarToast('Status Atualizado', response.mensagem, 'success');
        
        await carregarBarbeiros();
        if (appState.currentSection === 'barbeiros') {
            renderizarListaBarbeiros();
        }
        
    } catch (error) {
        console.error('❌ Erro ao alterar status do barbeiro:', error);
    }
}

function verFilaBarbeiro(barbeiroId) {
    /**
     * Navega para a fila de um barbeiro específico.
     * 
     * @param {number} barbeiroId - ID do barbeiro
     */
    
    navegarPara('fila');
    // Aqui poderia implementar filtro por barbeiro específico
}

async function exportarCSV() {
    /**
     * Exporta os dados de atendimentos em formato CSV.
     */
    
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/relatorios/exportar-csv`);
        
        if (!response.ok) {
            throw new Error('Erro ao exportar CSV');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `atendimentos_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        mostrarToast('Sucesso', 'Arquivo CSV exportado com sucesso', 'success');
        
    } catch (error) {
        console.error('❌ Erro ao exportar CSV:', error);
        mostrarToast('Erro', 'Falha ao exportar arquivo CSV', 'danger');
    }
}

// ===== UTILITÁRIOS =====
function limparFormulario() {
    /**
     * Limpa o formulário de cadastro de cliente.
     */
    
    document.getElementById('form-cadastro').reset();
}

function atualizarDados() {
    /**
     * Atualiza os dados da seção atual.
     */
    
    carregarDadosSecao(appState.currentSection);
    mostrarToast('Atualizado', 'Dados atualizados com sucesso', 'info');
}

function atualizarFila() {
    /**
     * Atualiza especificamente a fila de atendimento.
     */
    
    carregarFilaCompleta();
}

function mostrarLoading() {
    /**
     * Mostra o overlay de carregamento.
     */
    
    if (appState.isLoading) return;
    
    appState.isLoading = true;
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('d-none');
    }
}

function ocultarLoading() {
    /**
     * Oculta o overlay de carregamento.
     */
    
    appState.isLoading = false;
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('d-none');
    }
}

function mostrarToast(titulo, mensagem, tipo = 'info') {
    /**
     * Mostra uma notificação toast.
     * 
     * @param {string} titulo - Título da notificação
     * @param {string} mensagem - Mensagem da notificação
     * @param {string} tipo - Tipo da notificação (success, danger, warning, info)
     */
    
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toastId = `toast-${Date.now()}`;
    const iconMap = {
        success: 'fas fa-check-circle text-success',
        danger: 'fas fa-exclamation-circle text-danger',
        warning: 'fas fa-exclamation-triangle text-warning',
        info: 'fas fa-info-circle text-info'
    };
    
    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert">
            <div class="toast-header">
                <i class="${iconMap[tipo]} me-2"></i>
                <strong class="me-auto">${titulo}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${mensagem}
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: CONFIG.TOAST_DURATION
    });
    
    toast.show();
    
    // Remove o elemento após ser ocultado
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

function fecharModais() {
    /**
     * Fecha todos os modais abertos.
     */
    
    document.querySelectorAll('.modal.show').forEach(modal => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
            modalInstance.hide();
        }
    });
}

// ===== AUTO-REFRESH =====
function iniciarAutoRefresh() {
    /**
     * Inicia o sistema de atualização automática.
     */
    
    if (appState.refreshInterval) {
        clearInterval(appState.refreshInterval);
    }
    
    if (appState.autoRefresh) {
        appState.refreshInterval = setInterval(() => {
            if (appState.currentSection === 'fila') {
                carregarFilaCompleta();
            } else if (appState.currentSection === 'home') {
                carregarStatusSistema();
            }
        }, CONFIG.REFRESH_INTERVAL);
        
        console.log('🔄 Auto-refresh iniciado');
    }
}

function pararAutoRefresh() {
    /**
     * Para o sistema de atualização automática.
     */
    
    if (appState.refreshInterval) {
        clearInterval(appState.refreshInterval);
        appState.refreshInterval = null;
        console.log('⏹️ Auto-refresh parado');
    }
}

// ===== CLEANUP =====
window.addEventListener('beforeunload', function() {
    /**
     * Cleanup antes de sair da página.
     */
    
    pararAutoRefresh();
});

// ===== EXPOSIÇÃO DE FUNÇÕES GLOBAIS =====
// Funções que precisam ser acessíveis globalmente para eventos onclick
window.navegarPara = navegarPara;
window.cadastrarCliente = cadastrarCliente;
window.criarBarbeiro = criarBarbeiro;
window.chamarProximoCliente = chamarProximoCliente;
window.concluirAtendimento = concluirAtendimento;
window.cancelarCliente = cancelarCliente;
window.alternarStatusBarbeiro = alternarStatusBarbeiro;
window.verFilaBarbeiro = verFilaBarbeiro;
window.exportarCSV = exportarCSV;
window.limparFormulario = limparFormulario;
window.atualizarDados = atualizarDados;
window.atualizarFila = atualizarFila;

console.log('📱 Sistema de Fila Digital - Frontend carregado com sucesso!');



async function removerBarbeiro(barbeiroId) {
    /**
     * Remove um barbeiro do sistema.
     * 
     * @param {number} barbeiroId - ID do barbeiro
     */
    
    if (!confirm("Tem certeza que deseja remover este barbeiro? Esta ação é irreversível e removerá todos os dados associados a ele.")) {
        return;
    }
    
    try {
        const response = await apiCall(`/barbeiros/${barbeiroId}`, {
            method: 'DELETE'
        });
        
        mostrarToast('Sucesso', response.mensagem, 'success');
        
        await carregarBarbeiros();
        if (appState.currentSection === 'barbeiros') {
            renderizarListaBarbeiros();
        }
        
    } catch (error) {
        console.error('❌ Erro ao remover barbeiro:', error);
    }
}

// Adicionando a função ao escopo global
window.removerBarbeiro = removerBarbeiro;


