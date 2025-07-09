# -*- coding: utf-8 -*-
"""
Sistema de Fila Digital para Barbearia
Rotas da API: Clientes

Este arquivo contém todas as rotas da API REST relacionadas
ao gerenciamento de clientes e fila no sistema.

ATENÇÃO: Este código é propriedade intelectual protegida.
Uso não autorizado é proibido por lei.
"""

from flask import Blueprint, jsonify, request
from src.models.user import db
from src.models.cliente import Cliente
from src.models.barbeiro import Barbeiro
from src.models.atendimento import Atendimento
from datetime import datetime

# Criação do blueprint para as rotas de clientes
cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/clientes', methods=['POST'])
def cadastrar_cliente():
    """
    Cadastra um novo cliente na fila da barbearia.
    
    Endpoint: POST /api/clientes
    
    Body (JSON):
    {
        "nome": "Nome do Cliente",
        "numero_ficha": 123,
        "barbeiro_id": 1
    }
    
    Returns:
        JSON: Dados do cliente cadastrado e posição na fila
    """
    try:
        # Obtém os dados do corpo da requisição
        dados = request.get_json()
        
        # Validação dos dados obrigatórios
        campos_obrigatorios = ['nome', 'numero_ficha', 'barbeiro_id']
        for campo in campos_obrigatorios:
            if not dados or campo not in dados:
                return jsonify({
                    'erro': f'Campo {campo} é obrigatório',
                    'status': 'erro'
                }), 400
        
        nome = dados['nome'].strip()
        numero_ficha = dados['numero_ficha']
        barbeiro_id = dados['barbeiro_id']
        
        # Validações específicas
        if not nome or len(nome) < 2:
            return jsonify({
                'erro': 'Nome deve ter pelo menos 2 caracteres',
                'status': 'erro'
            }), 400
        
        if not isinstance(numero_ficha, int) or numero_ficha <= 0:
            return jsonify({
                'erro': 'Número da ficha deve ser um número inteiro positivo',
                'status': 'erro'
            }), 400
        
        # Verifica se o barbeiro existe e está ativo
        barbeiro = Barbeiro.query.get(barbeiro_id)
        if not barbeiro:
            return jsonify({
                'erro': 'Barbeiro não encontrado',
                'status': 'erro'
            }), 404
        
        if not barbeiro.ativo:
            return jsonify({
                'erro': 'Barbeiro não está ativo no momento',
                'status': 'erro'
            }), 400
        
        # Verifica se o número da ficha já está em uso
        ficha_existente = Cliente.query.filter_by(numero_ficha=numero_ficha).first()
        if ficha_existente and ficha_existente.status in ['aguardando', 'atendendo']:
            return jsonify({
                'erro': 'Número da ficha já está em uso',
                'status': 'erro'
            }), 409
        
        # Calcula a posição na fila
        clientes_na_fila = Cliente.query.filter_by(
            barbeiro_id=barbeiro_id,
            status='aguardando'
        ).count()
        
        posicao_fila = clientes_na_fila + 1
        
        # Cria o novo cliente
        novo_cliente = Cliente(
            nome=nome,
            numero_ficha=numero_ficha,
            barbeiro_id=barbeiro_id,
            posicao_fila=posicao_fila
        )
        
        # Salva no banco de dados
        db.session.add(novo_cliente)
        db.session.commit()
        
        return jsonify({
            'cliente': novo_cliente.to_dict(),
            'barbeiro': barbeiro.to_dict(),
            'posicao_fila': posicao_fila,
            'mensagem': f'Cliente {nome} cadastrado com sucesso na fila do {barbeiro.nome}',
            'status': 'sucesso'
        }), 201
        
    except Exception as e:
        # Rollback em caso de erro
        db.session.rollback()
        return jsonify({
            'erro': 'Erro interno do servidor',
            'detalhes': str(e),
            'status': 'erro'
        }), 500

@cliente_bp.route('/clientes/<int:cliente_id>', methods=['GET'])
def obter_cliente(cliente_id):
    """
    Obtém os dados de um cliente específico.
    
    Endpoint: GET /api/clientes/<id>
    
    Args:
        cliente_id (int): ID do cliente
        
    Returns:
        JSON: Dados do cliente
    """
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        barbeiro = Barbeiro.query.get(cliente.barbeiro_id)
        
        return jsonify({
            'cliente': cliente.to_dict(),
            'barbeiro': barbeiro.to_dict() if barbeiro else None,
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'erro': 'Cliente não encontrado',
            'status': 'erro'
        }), 404

@cliente_bp.route('/clientes/ficha/<int:numero_ficha>', methods=['GET'])
def obter_cliente_por_ficha(numero_ficha):
    """
    Obtém os dados de um cliente pelo número da ficha.
    
    Endpoint: GET /api/clientes/ficha/<numero>
    
    Args:
        numero_ficha (int): Número da ficha do cliente
        
    Returns:
        JSON: Dados do cliente e sua posição na fila
    """
    try:
        cliente = Cliente.query.filter_by(numero_ficha=numero_ficha).first()
        
        if not cliente:
            return jsonify({
                'erro': 'Cliente com esta ficha não encontrado',
                'status': 'erro'
            }), 404
        
        barbeiro = Barbeiro.query.get(cliente.barbeiro_id)
        
        # Se o cliente está aguardando, calcula a posição atual na fila
        if cliente.status == 'aguardando':
            posicao_atual = Cliente.query.filter(
                Cliente.barbeiro_id == cliente.barbeiro_id,
                Cliente.status == 'aguardando',
                Cliente.data_entrada < cliente.data_entrada
            ).count() + 1
            
            cliente.posicao_fila = posicao_atual
            db.session.commit()
        
        return jsonify({
            'cliente': cliente.to_dict(),
            'barbeiro': barbeiro.to_dict() if barbeiro else None,
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'erro': 'Erro ao buscar cliente',
            'detalhes': str(e),
            'status': 'erro'
        }), 500

@cliente_bp.route('/clientes/<int:cliente_id>/concluir', methods=['PUT'])
def concluir_atendimento_cliente(cliente_id):
    """
    Marca o atendimento de um cliente como concluído.
    
    Endpoint: PUT /api/clientes/<id>/concluir
    
    Args:
        cliente_id (int): ID do cliente
        
    Returns:
        JSON: Confirmação da conclusão do atendimento
    """
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        
        if cliente.status != 'atendendo':
            return jsonify({
                'erro': 'Cliente não está sendo atendido no momento',
                'status': 'erro'
            }), 400
        
        # Cria o registro de atendimento
        atendimento = Atendimento(
            cliente_id=cliente.id,
            barbeiro_id=cliente.barbeiro_id,
            numero_ficha=cliente.numero_ficha,
            nome_cliente=cliente.nome,
            data_entrada=cliente.data_entrada
        )
        
        # Finaliza o atendimento
        atendimento.finalizar_atendimento()
        
        # Marca o cliente como concluído
        cliente.concluir_atendimento()
        
        # Salva no banco de dados
        db.session.add(atendimento)
        db.session.commit()
        
        # Atualiza as posições na fila do barbeiro
        atualizar_posicoes_fila(cliente.barbeiro_id)
        
        return jsonify({
            'cliente': cliente.to_dict(),
            'atendimento': atendimento.to_dict(),
            'mensagem': f'Atendimento do cliente {cliente.nome} (Ficha {cliente.numero_ficha}) foi concluído',
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'erro': 'Erro ao concluir atendimento',
            'detalhes': str(e),
            'status': 'erro'
        }), 500

@cliente_bp.route('/clientes/<int:cliente_id>/cancelar', methods=['PUT'])
def cancelar_atendimento_cliente(cliente_id):
    """
    Cancela o atendimento de um cliente.
    
    Endpoint: PUT /api/clientes/<id>/cancelar
    
    Args:
        cliente_id (int): ID do cliente
        
    Returns:
        JSON: Confirmação do cancelamento
    """
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        
        if cliente.status == 'concluido':
            return jsonify({
                'erro': 'Atendimento já foi concluído',
                'status': 'erro'
            }), 400
        
        barbeiro_id = cliente.barbeiro_id
        
        # Cancela o atendimento
        cliente.cancelar_atendimento()
        db.session.commit()
        
        # Atualiza as posições na fila do barbeiro
        atualizar_posicoes_fila(barbeiro_id)
        
        return jsonify({
            'cliente': cliente.to_dict(),
            'mensagem': f'Atendimento do cliente {cliente.nome} (Ficha {cliente.numero_ficha}) foi cancelado',
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'erro': 'Erro ao cancelar atendimento',
            'detalhes': str(e),
            'status': 'erro'
        }), 500

@cliente_bp.route('/fila', methods=['GET'])
def obter_fila_completa():
    """
    Obtém a fila completa de todos os barbeiros.
    
    Endpoint: GET /api/fila
    
    Returns:
        JSON: Fila completa organizada por barbeiro
    """
    try:
        # Busca todos os barbeiros ativos
        barbeiros = Barbeiro.query.filter_by(ativo=True).all()
        
        fila_completa = {}
        
        for barbeiro in barbeiros:
            # Busca clientes aguardando este barbeiro
            clientes_fila = Cliente.query.filter_by(
                barbeiro_id=barbeiro.id,
                status='aguardando'
            ).order_by(Cliente.data_entrada.asc()).all()
            
            # Atualiza posições na fila
            for i, cliente in enumerate(clientes_fila, 1):
                cliente.posicao_fila = i
            
            # Cliente sendo atendido
            cliente_atendendo = Cliente.query.filter_by(
                barbeiro_id=barbeiro.id,
                status='atendendo'
            ).first()
            
            fila_completa[barbeiro.nome] = {
                'barbeiro': barbeiro.to_dict(),
                'fila_aguardando': [cliente.to_dict() for cliente in clientes_fila],
                'cliente_atendendo': cliente_atendendo.to_dict() if cliente_atendendo else None,
                'total_fila': len(clientes_fila)
            }
        
        # Salva as atualizações de posição
        db.session.commit()
        
        return jsonify({
            'fila_completa': fila_completa,
            'barbeiros_ativos': len(barbeiros),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'erro': 'Erro ao obter fila completa',
            'detalhes': str(e),
            'status': 'erro'
        }), 500

def atualizar_posicoes_fila(barbeiro_id):
    """
    Função auxiliar para atualizar as posições na fila de um barbeiro.
    
    Args:
        barbeiro_id (int): ID do barbeiro
    """
    try:
        # Busca todos os clientes aguardando este barbeiro
        clientes_fila = Cliente.query.filter_by(
            barbeiro_id=barbeiro_id,
            status='aguardando'
        ).order_by(Cliente.data_entrada.asc()).all()
        
        # Atualiza as posições
        for i, cliente in enumerate(clientes_fila, 1):
            cliente.posicao_fila = i
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        raise e

