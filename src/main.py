# -*- coding: utf-8 -*-
"""
Sistema de Fila Digital para Barbearia
Arquivo Principal da Aplicação

Este é o ponto de entrada principal do sistema de fila digital.
Configura a aplicação Flask, rotas, banco de dados e middleware.

ATENÇÃO: Este código é propriedade intelectual protegida.
Uso não autorizado é proibido por lei.
"""

import os
import sys
from datetime import datetime

# Configuração do path para importações
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.config import get_config, verificar_licenca, MENSAGEM_PROTECAO

# Importação das rotas (blueprints)
from src.routes.user import user_bp
from src.routes.barbeiro import barbeiro_bp
from src.routes.cliente import cliente_bp
from src.routes.atendimento import atendimento_bp

def criar_aplicacao():
    """
    Factory function para criar e configurar a aplicação Flask.
    
    Esta função centraliza toda a configuração da aplicação,
    incluindo banco de dados, rotas, middleware e segurança.
    
    Returns:
        Flask: Instância configurada da aplicação Flask
    """
    
    # Verificação de licença (proteção básica)
    if not verificar_licenca():
        print("ERRO: Licença não autorizada!")
        print(MENSAGEM_PROTECAO)
        sys.exit(1)
    
    # Criação da instância Flask
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Carregamento das configurações
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Configuração do CORS (Cross-Origin Resource Sharing)
    # Permite que o frontend acesse a API de qualquer origem
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Inicialização do banco de dados
    db.init_app(app)
    
    # Criação das tabelas do banco de dados
    with app.app_context():
        db.create_all()
        
        # Inserção de dados iniciais (barbeiros padrão)
        inserir_dados_iniciais()
    
    # Registro dos blueprints (rotas da API)
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(barbeiro_bp, url_prefix='/api')
    app.register_blueprint(cliente_bp, url_prefix='/api')
    app.register_blueprint(atendimento_bp, url_prefix='/api')
    
    # Configuração de rotas especiais
    configurar_rotas_especiais(app)
    
    # Configuração de handlers de erro
    configurar_handlers_erro(app)
    
    # Middleware personalizado
    configurar_middleware(app)
    
    return app

def inserir_dados_iniciais():
    """
    Insere dados iniciais no banco de dados se não existirem.
    
    Esta função cria barbeiros padrão para facilitar os testes
    e demonstração do sistema.
    """
    from src.models.barbeiro import Barbeiro
    
    try:
        # Verifica se já existem barbeiros cadastrados
        if Barbeiro.query.count() == 0:
            # Criação de barbeiros padrão
            barbeiros_padrao = [
                Barbeiro(nome='João Silva'),
                Barbeiro(nome='Pedro Santos'),
                Barbeiro(nome='Carlos Oliveira')
            ]
            
            for barbeiro in barbeiros_padrao:
                db.session.add(barbeiro)
            
            db.session.commit()
            print("✓ Barbeiros padrão criados com sucesso!")
            
    except Exception as e:
        print(f"Erro ao inserir dados iniciais: {e}")
        db.session.rollback()

def configurar_rotas_especiais(app):
    """
    Configura rotas especiais da aplicação.
    
    Args:
        app (Flask): Instância da aplicação Flask
    """
    
    @app.route('/api/status', methods=['GET'])
    def status_sistema():
        """
        Endpoint para verificar o status do sistema.
        
        Returns:
            JSON: Informações sobre o status do sistema
        """
        from src.models.barbeiro import Barbeiro
        from src.models.cliente import Cliente
        from src.config import SISTEMA_NOME, SISTEMA_VERSAO, SISTEMA_AUTOR
        
        try:
            # Contadores básicos
            total_barbeiros = Barbeiro.query.count()
            barbeiros_ativos = Barbeiro.query.filter_by(ativo=True).count()
            clientes_aguardando = Cliente.query.filter_by(status='aguardando').count()
            clientes_atendendo = Cliente.query.filter_by(status='atendendo').count()
            
            return jsonify({
                'sistema': {
                    'nome': SISTEMA_NOME,
                    'versao': SISTEMA_VERSAO,
                    'autor': SISTEMA_AUTOR,
                    'status': 'online',
                    'timestamp': datetime.utcnow().isoformat()
                },
                'estatisticas': {
                    'total_barbeiros': total_barbeiros,
                    'barbeiros_ativos': barbeiros_ativos,
                    'clientes_aguardando': clientes_aguardando,
                    'clientes_atendendo': clientes_atendendo
                },
                'banco_dados': {
                    'status': 'conectado',
                    'tipo': 'SQLite'
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'sistema': {
                    'nome': SISTEMA_NOME,
                    'versao': SISTEMA_VERSAO,
                    'status': 'erro'
                },
                'erro': str(e)
            }), 500
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def servir_frontend(path):
        """
        Serve os arquivos do frontend (SPA - Single Page Application).
        
        Esta rota captura todas as requisições que não são da API
        e serve o frontend React ou os arquivos estáticos.
        
        Args:
            path (str): Caminho solicitado
            
        Returns:
            File: Arquivo solicitado ou index.html para rotas SPA
        """
        static_folder_path = app.static_folder
        
        if static_folder_path is None:
            return jsonify({
                'erro': 'Pasta de arquivos estáticos não configurada',
                'status': 'erro'
            }), 404
        
        # Se o arquivo existe, serve diretamente
        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            # Para rotas SPA, sempre serve o index.html
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return jsonify({
                    'erro': 'Arquivo index.html não encontrado',
                    'mensagem': 'Certifique-se de que o frontend foi compilado corretamente',
                    'status': 'erro'
                }), 404

def configurar_handlers_erro(app):
    """
    Configura handlers personalizados para erros HTTP.
    
    Args:
        app (Flask): Instância da aplicação Flask
    """
    
    @app.errorhandler(404)
    def erro_nao_encontrado(error):
        """Handler para erro 404 - Não encontrado"""
        return jsonify({
            'erro': 'Recurso não encontrado',
            'codigo': 404,
            'status': 'erro'
        }), 404
    
    @app.errorhandler(500)
    def erro_interno_servidor(error):
        """Handler para erro 500 - Erro interno do servidor"""
        return jsonify({
            'erro': 'Erro interno do servidor',
            'codigo': 500,
            'status': 'erro'
        }), 500
    
    @app.errorhandler(400)
    def erro_requisicao_invalida(error):
        """Handler para erro 400 - Requisição inválida"""
        return jsonify({
            'erro': 'Requisição inválida',
            'codigo': 400,
            'status': 'erro'
        }), 400

def configurar_middleware(app):
    """
    Configura middleware personalizado da aplicação.
    
    Args:
        app (Flask): Instância da aplicação Flask
    """
    
    @app.before_request
    def antes_requisicao():
        """
        Middleware executado antes de cada requisição.
        
        Pode ser usado para logging, autenticação, etc.
        """
        # Log básico das requisições (apenas em desenvolvimento)
        if app.config.get('DEBUG'):
            from flask import request
            print(f"[{datetime.utcnow()}] {request.method} {request.path}")
    
    @app.after_request
    def depois_requisicao(response):
        """
        Middleware executado depois de cada requisição.
        
        Args:
            response: Resposta HTTP
            
        Returns:
            Response: Resposta modificada
        """
        # Adiciona headers de segurança
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response

# Criação da instância da aplicação
app = criar_aplicacao()

if __name__ == '__main__':
    """
    Ponto de entrada principal da aplicação.
    
    Executa o servidor Flask em modo de desenvolvimento
    ou produção dependendo das configurações.
    """
    
    print("=" * 60)
    print("🔥 SISTEMA DE FILA DIGITAL PARA BARBEARIA")
    print("=" * 60)
    print(f"📅 Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🌐 Servidor: http://0.0.0.0:5000")
    print(f"🔧 Modo: {'Desenvolvimento' if app.config.get('DEBUG') else 'Produção'}")
    print("=" * 60)
    print()
    print("📋 ENDPOINTS DISPONÍVEIS:")
    print("   • GET  /api/status           - Status do sistema")
    print("   • GET  /api/barbeiros        - Lista barbeiros")
    print("   • POST /api/barbeiros        - Criar barbeiro")
    print("   • GET  /api/barbeiros/{id}/fila - Fila do barbeiro")
    print("   • POST /api/clientes         - Cadastrar cliente")
    print("   • GET  /api/fila             - Fila completa")
    print("   • GET  /api/atendimentos     - Histórico")
    print("   • GET  /api/relatorios/exportar-csv - Exportar CSV")
    print("=" * 60)
    print()
    
    # Execução do servidor
    app.run(
        host='0.0.0.0',  # Permite acesso externo
        port=5000,       # Porta padrão
        debug=app.config.get('DEBUG', False),  # Modo debug baseado na configuração
        threaded=True    # Suporte a múltiplas requisições simultâneas
    )
