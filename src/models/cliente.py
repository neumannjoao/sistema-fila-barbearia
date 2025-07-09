# -*- coding: utf-8 -*-
"""
Sistema de Fila Digital para Barbearia
Modelo de Dados: Cliente

Este arquivo contém a definição do modelo de dados para representar
os clientes na fila da barbearia, incluindo informações sobre
fichas físicas e posicionamento na fila.

ATENÇÃO: Este código é propriedade intelectual protegida.
Uso não autorizado é proibido por lei.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Cliente(db.Model):
    """
    Classe modelo para representar um cliente na fila da barbearia.
    
    Esta classe gerencia todas as informações relacionadas aos clientes
    que estão aguardando atendimento, incluindo o número da ficha física,
    barbeiro preferido e posição atual na fila.
    
    Atributos da tabela no banco de dados:
        id (Integer): Chave primária única para identificar cada cliente
        nome (String): Nome completo do cliente (máximo 100 caracteres)
        numero_ficha (Integer): Número da ficha física entregue ao cliente
        barbeiro_id (Integer): Chave estrangeira referenciando o barbeiro preferido
        data_entrada (DateTime): Data e hora de entrada na fila
        status (String): Status atual do atendimento
        posicao_fila (Integer): Posição atual do cliente na fila do barbeiro
    
    Status possíveis:
        - 'aguardando': Cliente está na fila aguardando atendimento
        - 'atendendo': Cliente está sendo atendido no momento
        - 'concluido': Atendimento foi finalizado
        - 'cancelado': Cliente desistiu ou não compareceu
    """
    
    # Nome da tabela no banco de dados SQLite
    __tablename__ = 'clientes'
    
    # Definição das colunas da tabela
    id = db.Column(db.Integer, primary_key=True, comment='Identificador único do cliente')
    nome = db.Column(db.String(100), nullable=False, comment='Nome completo do cliente')
    numero_ficha = db.Column(db.Integer, unique=True, nullable=False, comment='Número da ficha física')
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=False, 
                           comment='ID do barbeiro preferido')
    data_entrada = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                           comment='Data e hora de entrada na fila')
    status = db.Column(db.String(20), default='aguardando', nullable=False,
                      comment='Status atual do atendimento')
    posicao_fila = db.Column(db.Integer, nullable=True, comment='Posição atual na fila')
    
    # Relacionamento um-para-muitos com a tabela de atendimentos
    # Um cliente pode ter vários atendimentos (histórico)
    atendimentos = db.relationship('Atendimento', backref='cliente', lazy=True)

    def __repr__(self):
        """
        Representação em string do objeto Cliente para debug e logs.
        
        Returns:
            str: Representação formatada do cliente
        """
        return f'<Cliente ID:{self.id} Nome:{self.nome} Ficha:{self.numero_ficha} Status:{self.status}>'

    def to_dict(self):
        """
        Converte o objeto Cliente para um dicionário Python.
        
        Este método é usado para serializar os dados do cliente
        para envio via API REST em formato JSON.
        
        Returns:
            dict: Dicionário contendo os dados do cliente
        """
        return {
            'id': self.id,
            'nome': self.nome,
            'numero_ficha': self.numero_ficha,
            'barbeiro_id': self.barbeiro_id,
            'data_entrada': self.data_entrada.isoformat() if self.data_entrada else None,
            'status': self.status,
            'posicao_fila': self.posicao_fila
        }
    
    def iniciar_atendimento(self):
        """
        Marca o cliente como sendo atendido no momento.
        
        Este método atualiza o status do cliente para 'atendendo'
        e remove sua posição da fila.
        """
        self.status = 'atendendo'
        self.posicao_fila = None
    
    def concluir_atendimento(self):
        """
        Marca o atendimento do cliente como concluído.
        
        Este método atualiza o status do cliente para 'concluido'
        indicando que o atendimento foi finalizado.
        """
        self.status = 'concluido'
    
    def cancelar_atendimento(self):
        """
        Cancela o atendimento do cliente.
        
        Este método é usado quando o cliente desiste ou não comparece
        para o atendimento.
        """
        self.status = 'cancelado'
        self.posicao_fila = None
    
    def atualizar_posicao_fila(self, nova_posicao):
        """
        Atualiza a posição do cliente na fila.
        
        Args:
            nova_posicao (int): Nova posição do cliente na fila
        """
        self.posicao_fila = nova_posicao

