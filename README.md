# 🔥 Sistema de Fila Digital para Barbearia

## 📋 Descrição do Projeto

Sistema web completo para gerenciamento de fila digital em barbearias, desenvolvido com Flask (Python) e interface web moderna. O sistema permite organizar filas por barbeiro, controlar atendimentos em tempo real e gerar relatórios detalhados.

**⚠️ ATENÇÃO: Este código é propriedade intelectual protegida. Uso não autorizado é proibido por lei.**

## ✨ Funcionalidades Principais

### 🎯 Para a Recepção
- ✅ Cadastro rápido de clientes na fila
- ✅ Seleção de barbeiro preferido
- ✅ Geração automática de posição na fila
- ✅ Interface intuitiva e responsiva

### 📺 Para Exibição (TV)
- ✅ Visualização em tempo real das filas
- ✅ Destaque do número da ficha para o painel físico
- ✅ Atualização automática a cada 5 segundos
- ✅ Design otimizado para visualização à distância

### 📱 Para os Barbeiros
- ✅ Controle individual da própria fila
- ✅ Chamada do próximo cliente
- ✅ Finalização de atendimentos
- ✅ Interface mobile-friendly

### 📊 Relatórios e Análises
- ✅ Histórico completo de atendimentos
- ✅ Estatísticas de tempo de espera
- ✅ Exportação de dados em CSV
- ✅ Métricas de performance por barbeiro

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.11** - Linguagem principal
- **Flask 3.1.1** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados local
- **Flask-CORS** - Suporte a CORS

### Frontend
- **HTML5** - Estrutura das páginas
- **CSS3** - Estilos modernos e responsivos
- **JavaScript ES6+** - Interatividade e comunicação com API
- **Bootstrap 5.3** - Framework CSS
- **Font Awesome 6.4** - Ícones
- **Google Fonts** - Tipografia (Poppins)

### Recursos Especiais
- **SPA (Single Page Application)** - Navegação fluida
- **API REST** - Comunicação backend/frontend
- **Auto-refresh** - Atualização automática em tempo real
- **Responsive Design** - Compatível com desktop e mobile
- **Toast Notifications** - Feedback visual para o usuário

## 📁 Estrutura do Projeto

```
sistema-fila-barbearia/
├── venv/                          # Ambiente virtual Python
├── src/                           # Código fonte principal
│   ├── models/                    # Modelos de dados
│   │   ├── user.py               # Configuração do SQLAlchemy
│   │   ├── barbeiro.py           # Modelo Barbeiro
│   │   ├── cliente.py            # Modelo Cliente
│   │   └── atendimento.py        # Modelo Atendimento
│   ├── routes/                    # Rotas da API REST
│   │   ├── user.py               # Rotas de usuário (template)
│   │   ├── barbeiro.py           # API de barbeiros
│   │   ├── cliente.py            # API de clientes
│   │   └── atendimento.py        # API de atendimentos/relatórios
│   ├── static/                    # Arquivos estáticos (frontend)
│   │   ├── css/
│   │   │   └── style.css         # Estilos personalizados
│   │   ├── js/
│   │   │   └── app.js            # JavaScript principal
│   │   └── index.html            # Página principal
│   ├── database/                  # Banco de dados
│   │   └── app.db                # Arquivo SQLite
│   ├── config.py                 # Configurações do sistema
│   └── main.py                   # Arquivo principal da aplicação
├── requirements.txt              # Dependências Python
└── README.md                     # Esta documentação
```

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Git (opcional, para clonagem)

### Passo 1: Preparação do Ambiente

```bash
# Clone ou extraia o projeto
cd sistema-fila-barbearia

# Ative o ambiente virtual (já criado)
source venv/bin/activate

# Verifique se as dependências estão instaladas
pip install -r requirements.txt
```

### Passo 2: Configuração do Banco de Dados

O sistema usa SQLite e cria automaticamente:
- ✅ Tabelas necessárias na primeira execução
- ✅ Barbeiros padrão (João Silva, Pedro Santos, Carlos Oliveira)
- ✅ Estrutura completa do banco de dados

### Passo 3: Execução do Sistema

```bash
# Ative o ambiente virtual
source venv/bin/activate

# Execute o sistema
python src/main.py
```

O sistema estará disponível em: **http://localhost:5000**

## 📖 Manual de Uso

### 🏠 Página Inicial
- Visão geral do sistema
- Status em tempo real
- Navegação rápida para funcionalidades

### 👥 Cadastro de Clientes

1. **Acesse a seção "Cadastro"**
2. **Preencha os dados:**
   - Nome completo do cliente
   - Número da ficha física
   - Barbeiro preferido
3. **Clique em "Cadastrar na Fila"**
4. **Cliente é automaticamente posicionado na fila**

### 📺 Visualização da Fila (Para TV)

1. **Acesse a seção "Fila"**
2. **Visualize em tempo real:**
   - Filas organizadas por barbeiro
   - Números das fichas em destaque
   - Posição de cada cliente
   - Cliente em atendimento
3. **Atualização automática a cada 5 segundos**

### 📱 Controle pelos Barbeiros

1. **Acesse a seção "Fila"**
2. **Para cada cliente na fila:**
   - **▶️ Chamar próximo:** Inicia atendimento
   - **✅ Concluir:** Finaliza atendimento
   - **❌ Cancelar:** Remove da fila
3. **Acompanhe estatísticas em tempo real**

### 👨‍💼 Gerenciamento de Barbeiros

1. **Acesse a seção "Barbeiros"**
2. **Funcionalidades disponíveis:**
   - ➕ Cadastrar novo barbeiro
   - ⏸️ Ativar/Desativar barbeiro
   - 👥 Ver fila específica
   - 📊 Acompanhar performance

### 📊 Relatórios e Estatísticas

1. **Acesse a seção "Relatórios"**
2. **Visualize:**
   - Estatísticas do dia atual
   - Tempo médio de espera
   - Tempo médio de atendimento
   - Performance por barbeiro
3. **Exporte dados em CSV**

## 🔧 Configurações Avançadas

### Personalização do Sistema

Edite o arquivo `src/config.py` para ajustar:

```python
# Intervalo de atualização (em segundos)
REFRESH_INTERVAL = 5

# Configurações de segurança
SECRET_KEY = 'sua-chave-secreta-aqui'

# Configurações do banco de dados
SQLALCHEMY_DATABASE_URI = 'sqlite:///caminho/para/banco.db'
```

### Configuração para Produção

1. **Desative o modo debug:**
```python
DEBUG = False
```

2. **Configure chave secreta segura:**
```python
SECRET_KEY = 'chave-muito-segura-e-aleatoria'
```

3. **Use servidor WSGI (Gunicorn):**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

## 🌐 API REST - Endpoints Disponíveis

### Status do Sistema
- `GET /api/status` - Informações gerais do sistema

### Barbeiros
- `GET /api/barbeiros` - Lista todos os barbeiros
- `POST /api/barbeiros` - Cria novo barbeiro
- `GET /api/barbeiros/{id}/fila` - Fila específica do barbeiro
- `POST /api/barbeiros/{id}/proximo` - Chama próximo cliente
- `PUT /api/barbeiros/{id}/ativar` - Ativa barbeiro
- `PUT /api/barbeiros/{id}/desativar` - Desativa barbeiro

### Clientes
- `POST /api/clientes` - Cadastra cliente na fila
- `GET /api/clientes/{id}` - Dados do cliente
- `GET /api/clientes/ficha/{numero}` - Busca por número da ficha
- `PUT /api/clientes/{id}/concluir` - Conclui atendimento
- `PUT /api/clientes/{id}/cancelar` - Cancela atendimento
- `GET /api/fila` - Fila completa de todos os barbeiros

### Relatórios
- `GET /api/atendimentos` - Lista atendimentos (com filtros)
- `GET /api/relatorios/estatisticas` - Estatísticas gerais
- `GET /api/relatorios/exportar-csv` - Exporta dados em CSV
- `GET /api/relatorios/resumo-diario` - Resumo do dia

## 🔒 Segurança e Proteção

### Medidas Implementadas
- ✅ **Validação de dados** em todas as entradas
- ✅ **Sanitização** de inputs do usuário
- ✅ **Headers de segurança** HTTP
- ✅ **CORS configurado** adequadamente
- ✅ **Tratamento de erros** robusto
- ✅ **Logs de auditoria** das operações

### Proteção do Código Fonte
- ✅ **Comentários em português** para proteção
- ✅ **Avisos de propriedade intelectual**
- ✅ **Estrutura preparada** para ofuscação
- ✅ **Configurações centralizadas** para deploy

## 🐛 Solução de Problemas

### Problemas Comuns

**❌ Erro: "Port already in use"**
```bash
# Encontre o processo usando a porta
lsof -i :5000
# Mate o processo
kill -9 [PID]
```

**❌ Erro: "Module not found"**
```bash
# Reinstale as dependências
pip install -r requirements.txt
```

**❌ Erro: "Database locked"**
```bash
# Pare o servidor e reinicie
# Verifique se não há múltiplas instâncias rodando
```

**❌ Interface não carrega**
- Verifique se o servidor está rodando
- Acesse http://localhost:5000
- Verifique o console do navegador para erros

### Logs e Debug

```bash
# Execute com logs detalhados
FLASK_DEBUG=1 python src/main.py

# Verifique logs do sistema
tail -f sistema_fila.log
```

## 📈 Performance e Otimização

### Recomendações
- ✅ **Máximo 50 clientes** simultâneos por barbeiro
- ✅ **Auto-refresh** pode ser desabilitado se necessário
- ✅ **Backup automático** do banco de dados
- ✅ **Limpeza periódica** de dados antigos

### Monitoramento
- Acompanhe uso de CPU e memória
- Monitore tamanho do banco de dados
- Verifique logs de erro regularmente

## 🔄 Backup e Recuperação

### Backup Manual
```bash
# Backup do banco de dados
cp src/database/app.db backup/app_$(date +%Y%m%d_%H%M%S).db

# Backup completo do sistema
tar -czf backup_sistema_$(date +%Y%m%d).tar.gz sistema-fila-barbearia/
```

### Restauração
```bash
# Restaurar banco de dados
cp backup/app_YYYYMMDD_HHMMSS.db src/database/app.db
```

## 📞 Suporte e Contato

### Informações do Sistema
- **Versão:** 1.0.0
- **Desenvolvido por:** IA Manus
- **Licença:** Propriedade Intelectual Protegida

### Para Suporte Técnico
- Verifique este README primeiro
- Consulte os logs de erro
- Documente o problema detalhadamente

## 📝 Changelog

### Versão 1.0.0 (2025-07-05)
- ✅ Implementação completa do sistema
- ✅ Interface web responsiva
- ✅ API REST completa
- ✅ Sistema de relatórios
- ✅ Exportação CSV
- ✅ Auto-refresh em tempo real
- ✅ Proteção de código fonte
- ✅ Documentação completa

## 🎯 Próximas Funcionalidades (Roadmap)

### Versão 1.1.0 (Planejada)
- 🔄 Notificações push para barbeiros
- 📱 App mobile nativo
- 🔐 Sistema de autenticação
- 📊 Dashboard avançado de analytics
- 🎨 Temas personalizáveis
- 💾 Backup automático na nuvem

### Versão 1.2.0 (Planejada)
- 📅 Sistema de agendamentos
- 💰 Integração com pagamentos
- 📧 Notificações por email/SMS
- 🏪 Suporte a múltiplas filiais
- 📈 Relatórios avançados
- 🔌 API para integrações externas

---

**© 2025 - Sistema de Fila Digital para Barbearia - Todos os direitos reservados**

*Este sistema foi desenvolvido com foco na usabilidade, performance e segurança. Para melhor experiência, utilize em navegadores modernos (Chrome, Firefox, Safari, Edge).*

