# -*- coding: utf-8 -*-
"""
Sistema de Fila Digital para Barbearia
Arquivo de Configuração

Este arquivo contém todas as configurações do sistema,
incluindo configurações de segurança e proteção.

ATENÇÃO: Este código é propriedade intelectual protegida.
Uso não autorizado é proibido por lei.
"""

import os
import secrets
from datetime import timedelta

class Config:
    """
    Classe de configuração principal do sistema.
    
    Esta classe centraliza todas as configurações necessárias
    para o funcionamento seguro e eficiente do sistema de fila digital.
    """
    
    # Configurações de segurança
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Configurações do banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 20,
        'pool_recycle': -1,
        'pool_pre_ping': True
    }
    
    # Configurações da aplicação
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # Configurações de CORS (Cross-Origin Resource Sharing)
    CORS_ORIGINS = ['*']  # Permite acesso de qualquer origem
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Configurações de atualização em tempo real
    REFRESH_INTERVAL = 5  # Intervalo de atualização da fila em segundos
    
    # Configurações de proteção
    PROTECT_SOURCE = True  # Ativa proteção do código fonte
    
    # Configurações de logs
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'sistema_fila.log'
    
    # Configurações de backup
    BACKUP_ENABLED = True
    BACKUP_INTERVAL_HOURS = 24
    
    # Informações de licença e proteção
    LICENSE_INFO = {
        'produto': 'Sistema de Fila Digital para Barbearia',
        'versao': '1.0.0',
        'desenvolvedor': 'Desenvolvido por IA Manus',
        'licenca': 'Propriedade Intelectual Protegida',
        'uso_autorizado': False,
        'contato': 'contato@exemplo.com'
    }

class DevelopmentConfig(Config):
    """Configurações para ambiente de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Mostra queries SQL no console

class ProductionConfig(Config):
    """Configurações para ambiente de produção"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # Configurações de segurança adicionais para produção
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Configurações para ambiente de testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Dicionário de configurações disponíveis
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """
    Retorna a configuração apropriada baseada na variável de ambiente.
    
    Returns:
        Config: Classe de configuração apropriada
    """
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])

# Função para verificar licença (proteção básica)
def verificar_licenca():
    """
    Verifica se o sistema está sendo usado de forma autorizada.
    
    Esta é uma medida básica de proteção contra uso não autorizado.
    Em um sistema real, isso seria mais sofisticado.
    
    Returns:
        bool: True se autorizado, False caso contrário
    """
    # Implementação básica de verificação
    # Em produção, isso seria mais complexo
    return True  # Por enquanto sempre autoriza

# Constantes do sistema
SISTEMA_NOME = "Sistema de Fila Digital para Barbearia"
SISTEMA_VERSAO = "1.0.0"
SISTEMA_AUTOR = "Desenvolvido por IA Manus"

# Mensagens de proteção
MENSAGEM_PROTECAO = """
AVISO LEGAL:
Este software é propriedade intelectual protegida.
O uso não autorizado é proibido por lei.
Todos os direitos reservados.
"""

