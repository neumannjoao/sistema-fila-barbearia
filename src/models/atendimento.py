# -*- coding: utf-8 -*-
"""
Sistema de Fila Digital para Barbearia
Modelo de Dados: Atendimento

Este arquivo contém a definição do modelo de dados para registrar
o histórico completo de atendimentos realizados na barbearia,
incluindo métricas de tempo e performance.

ATENÇÃO: Este código é propriedade intelectual protegida.
Uso não autorizado é proibido por lei.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Atendimento(db.Model):
    """
    Classe modelo para representar um atendimento realizado na barbearia.
    
    Esta classe armazena o histórico completo de todos os atendimentos,
    permitindo análises de performance, relatórios e controle de qualidade
    do serviço prestado pela barbearia.
    
    Atributos da tabela no banco de dados:
        id (Integer): Chave primária única para identificar cada atendimento
        cliente_id (Integer): Chave estrangeira referenciando o cliente
        barbeiro_id (Integer): Chave estrangeira referenciando o barbeiro
        numero_ficha (Integer): Número da ficha física do cliente
        nome_cliente (String): Nome do cliente (desnormalizado para relatórios)
        data_entrada (DateTime): Data e hora de entrada na fila
        data_inicio (DateTime): Data e hora de início do atendimento
        data_fim (DateTime): Data e hora de fim do atendimento
        tempo_espera (Integer): Tempo de espera em minutos
        tempo_atendimento (Integer): Tempo de atendimento em minutos
    
    Métricas calculadas:
        - Tempo de espera: Diferença entre entrada na fila e início do atendimento
        - Tempo de atendimento: Diferença entre início e fim do atendimento
        - Tempo total: Soma do tempo de espera e atendimento
    """
    
    # Nome da tabela no banco de dados SQLite
    __tablename__ = 'atendimentos'
    
    # Definição das colunas da tabela
    id = db.Column(db.Integer, primary_key=True, comment='Identificador único do atendimento')
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False,
                          comment='ID do cliente atendido')
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=False,
                           comment='ID do barbeiro que realizou o atendimento')
    numero_ficha = db.Column(db.Integer, nullable=False, comment='Número da ficha do cliente')
    nome_cliente = db.Column(db.String(100), nullable=False, comment='Nome do cliente')
    data_entrada = db.Column(db.DateTime, nullable=False, comment='Data e hora de entrada na fila')
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                           comment='Data e hora de início do atendimento')
    data_fim = db.Column(db.DateTime, nullable=True, comment='Data e hora de fim do atendimento')
    tempo_espera = db.Column(db.Integer, nullable=True, comment='Tempo de espera em minutos')
    tempo_atendimento = db.Column(db.Integer, nullable=True, comment='Tempo de atendimento em minutos')

    def __repr__(self):
        """
        Representação em string do objeto Atendimento para debug e logs.
        
        Returns:
            str: Representação formatada do atendimento
        """
        return f'<Atendimento ID:{self.id} Ficha:{self.numero_ficha} Cliente:{self.nome_cliente}>'

    def calcular_tempos(self):
        """
        Calcula automaticamente os tempos de espera e atendimento.
        
        Este método é chamado automaticamente quando o atendimento é finalizado
        para calcular as métricas de tempo baseadas nas datas registradas.
        
        Cálculos realizados:
        - Tempo de espera: data_inicio - data_entrada
        - Tempo de atendimento: data_fim - data_inicio
        """
        # Calcula o tempo de espera (entrada na fila até início do atendimento)
        if self.data_entrada and self.data_inicio:
            delta_espera = self.data_inicio - self.data_entrada
            self.tempo_espera = int(delta_espera.total_seconds() / 60)  # Converte para minutos
        
        # Calcula o tempo de atendimento (início até fim do atendimento)
        if self.data_inicio and self.data_fim:
            delta_atendimento = self.data_fim - self.data_inicio
            self.tempo_atendimento = int(delta_atendimento.total_seconds() / 60)  # Converte para minutos

    def finalizar_atendimento(self):
        """
        Finaliza o atendimento registrando a data/hora de fim.
        
        Este método marca o atendimento como concluído, registra o timestamp
        de finalização e calcula automaticamente as métricas de tempo.
        """
        self.data_fim = datetime.utcnow()
        self.calcular_tempos()

    def to_dict(self):
        """
        Converte o objeto Atendimento para um dicionário Python.
        
        Este método é usado para serializar os dados do atendimento
        para envio via API REST em formato JSON ou para exportação
        em relatórios CSV.
        
        Returns:
            dict: Dicionário contendo todos os dados do atendimento
        """
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'barbeiro_id': self.barbeiro_id,
            'numero_ficha': self.numero_ficha,
            'nome_cliente': self.nome_cliente,
            'data_entrada': self.data_entrada.isoformat() if self.data_entrada else None,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'tempo_espera': self.tempo_espera,
            'tempo_atendimento': self.tempo_atendimento,
            'tempo_total': (self.tempo_espera or 0) + (self.tempo_atendimento or 0)
        }
    
    def to_csv_row(self):
        """
        Converte o atendimento para uma linha de CSV para exportação.
        
        Returns:
            list: Lista com os valores formatados para CSV
        """
        return [
            self.id,
            self.numero_ficha,
            self.nome_cliente,
            self.barbeiro_id,
            self.data_entrada.strftime('%d/%m/%Y %H:%M:%S') if self.data_entrada else '',
            self.data_inicio.strftime('%d/%m/%Y %H:%M:%S') if self.data_inicio else '',
            self.data_fim.strftime('%d/%m/%Y %H:%M:%S') if self.data_fim else '',
            self.tempo_espera or 0,
            self.tempo_atendimento or 0,
            (self.tempo_espera or 0) + (self.tempo_atendimento or 0)
        ]

