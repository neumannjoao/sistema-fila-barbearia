# -*- coding: utf-8 -*-
"""
Sistema de Fila Digital para Barbearia
Modelo de Dados: Barbeiro

Este arquivo contém a definição do modelo de dados para representar
os barbeiros no sistema de fila digital da barbearia.

ATENÇÃO: Este código é propriedade intelectual protegida.
Uso não autorizado é proibido por lei.
"""

from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class Barbeiro(db.Model):
    """
    Classe modelo para representar um barbeiro no sistema de fila digital.
    
    Esta classe define a estrutura de dados para armazenar informações
    dos barbeiros que trabalham na barbearia, incluindo seu status
    de atividade e relacionamentos com atendimentos.
    
    Atributos da tabela no banco de dados:
        id (Integer): Chave primária única para identificar cada barbeiro
        nome (String): Nome completo do barbeiro (máximo 100 caracteres)
        ativo (Boolean): Indica se o barbeiro está ativo no sistema
    
    Relacionamentos:
        atendimentos: Lista de todos os atendimentos realizados por este barbeiro
    """
    
    # Nome da tabela no banco de dados SQLite
    __tablename__ = 'barbeiros'
    
    # Definição das colunas da tabela
    id = db.Column(db.Integer, primary_key=True, comment='Identificador único do barbeiro')
    nome = db.Column(db.String(100), unique=True, nullable=False, comment='Nome completo do barbeiro')
    ativo = db.Column(db.Boolean, default=True, nullable=False, comment='Status ativo/inativo do barbeiro')
    
    # Relacionamento um-para-muitos com a tabela de atendimentos
    # Um barbeiro pode ter vários atendimentos
    atendimentos = db.relationship('Atendimento', backref='barbeiro', lazy=True, 
                                 cascade='all, delete-orphan')

    def __repr__(self):
        """
        Representação em string do objeto Barbeiro para debug e logs.
        
        Returns:
            str: Representação formatada do barbeiro
        """
        return f'<Barbeiro ID:{self.id} Nome:{self.nome} Ativo:{self.ativo}>'

    def to_dict(self):
        """
        Converte o objeto Barbeiro para um dicionário Python.
        
        Este método é usado para serializar os dados do barbeiro
        para envio via API REST em formato JSON.
        
        Returns:
            dict: Dicionário contendo os dados do barbeiro
        """
        return {
            'id': self.id,
            'nome': self.nome,
            'ativo': self.ativo
        }
    
    def ativar(self):
        """
        Ativa o barbeiro no sistema.
        
        Este método define o status do barbeiro como ativo,
        permitindo que ele receba novos clientes na fila.
        """
        self.ativo = True
    
    def desativar(self):
        """
        Desativa o barbeiro no sistema.
        
        Este método define o status do barbeiro como inativo,
        impedindo que novos clientes sejam direcionados para sua fila.
        """
        self.ativo = False

