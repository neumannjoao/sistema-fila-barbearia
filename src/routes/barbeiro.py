# -*- coding: utf-8 -*-
"""
Sistema de Fila Digital para Barbearia
Rotas da API: Barbeiros

Este arquivo contém todas as rotas da API REST relacionadas
ao gerenciamento de barbeiros no sistema.

ATENÇÃO: Este código é propriedade intelectual protegida.
Uso não autorizado é proibido por lei.
"""

from flask import Blueprint, jsonify, request
from src.models.user import db
from src.models.barbeiro import Barbeiro
from src.models.cliente import Cliente
from datetime import datetime

# Criação do blueprint para as rotas de barbeiros
barbeiro_bp = Blueprint('barbeiro', __name__)

@barbeiro_bp.route('/barbeiros', methods=['GET'])
def listar_barbeiros():
    """
    Lista todos os barbeiros cadastrados no sistema.
    
    Endpoint: GET /api/barbeiros
    
    Returns:
        JSON: Lista com todos os barbeiros e seus dados
        
    Exemplo de resposta:
    {
        "barbeiros": [
            {
                "id": 1,
                "nome": "João Silva",
                "ativo": true
            }
        ],
        "total": 1
    }
    """
    try:
        # Busca todos os barbeiros no banco de dados
        barbeiros = Barbeiro.query.all()
        
        # Converte os objetos para dicionários
        barbeiros_data = [barbeiro.to_dict() for barbeiro in barbeiros]
        
        return jsonify({
            'barbeiros': barbeiros_data,
            'total': len(barbeiros_data),
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'erro': 'Erro interno do servidor',
            'detalhes': str(e),
            'status': 'erro'
        }), 500

@barbeiro_bp.route('/barbeiros', methods=['POST'])
def criar_barbeiro():
    """
    Cria um novo barbeiro no sistema.
    
    Endpoint: POST /api/barbeiros
    
    Body (JSON):
    {
        "nome": "Nome do Barbeiro"
    }
    
    Returns:
        JSON: Dados do barbeiro criado
    """
    try:
        # Obtém os dados do corpo da requisição
        dados = request.get_json()
        
        # Validação dos dados obrigatórios
        if not dados or 'nome' not in dados:
            return jsonify({
                'erro': 'Nome do barbeiro é obrigatório',
                'status': 'erro'
            }), 400
        
        nome = dados['nome'].strip()
        
        # Validação do nome
        if not nome or len(nome) < 2:
            return jsonify({
                'erro': 'Nome deve ter pelo menos 2 caracteres',
                'status': 'erro'
            }), 400
        
        # Verifica se já existe um barbeiro com este nome
        barbeiro_existente = Barbeiro.query.filter_by(nome=nome).first()
        if barbeiro_existente:
            return jsonify({
                'erro': 'Já existe um barbeiro com este nome',
                'status': 'erro'
            }), 409
        
        # Cria o novo barbeiro
        novo_barbeiro = Barbeiro(nome=nome)
        
        # Salva no banco de dados
        db.session.add(novo_barbeiro)
        db.session.commit()
        
        return jsonify({
            'barbeiro': novo_barbeiro.to_dict(),
            'mensagem': 'Barbeiro criado com sucesso',
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

@barbeiro_bp.route('/barbeiros/<int:barbeiro_id>', methods=['GET'])
def obter_barbeiro(barbeiro_id):
    """
    Obtém os dados de um barbeiro específico.
    
    Endpoint: GET /api/barbeiros/<id>
    
    Args:
        barbeiro_id (int): ID do barbeiro
        
    Returns:
        JSON: Dados do barbeiro
    """
    try:
        # Busca o barbeiro pelo ID
        barbeiro = Barbeiro.query.get_or_404(barbeiro_id)
        
        return jsonify({
            'barbeiro': barbeiro.to_dict(),
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'erro': 'Barbeiro não encontrado',
            'status': 'erro'
        }), 404

@barbeiro_bp.route('/barbeiros/<int:barbeiro_id>/fila', methods=['GET'])
def obter_fila_barbeiro(barbeiro_id):
    """
    Obtém a fila atual de um barbeiro específico.
    
    Endpoint: GET /api/barbeiros/<id>/fila
    
    Args:
        barbeiro_id (int): ID do barbeiro
        
    Returns:
        JSON: Lista de clientes na fila do barbeiro
    """
    try:
        # Verifica se o barbeiro existe
        barbeiro = Barbeiro.query.get_or_404(barbeiro_id)
        
        # Busca todos os clientes aguardando este barbeiro
        clientes_fila = Cliente.query.filter_by(
            barbeiro_id=barbeiro_id,
            status='aguardando'
        ).order_by(Cliente.data_entrada.asc()).all()
        
        # Atualiza as posições na fila
        for i, cliente in enumerate(clientes_fila, 1):
            cliente.posicao_fila = i
        
        # Salva as atualizações de posição
        db.session.commit()
        
        # Converte para dicionários
        fila_data = [cliente.to_dict() for cliente in clientes_fila]
        
        return jsonify({
            'barbeiro': barbeiro.to_dict(),
            'fila': fila_data,
            'total_fila': len(fila_data),
            'proximo_cliente': fila_data[0] if fila_data else None,
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'erro': 'Erro ao obter fila do barbeiro',
            'detalhes': str(e),
            'status': 'erro'
        }), 500

@barbeiro_bp.route('/barbeiros/<int:barbeiro_id>/proximo', methods=['POST'])
def chamar_proximo_cliente(barbeiro_id):
    """
    Chama o próximo cliente da fila do barbeiro.
    
    Endpoint: POST /api/barbeiros/<id>/proximo
    
    Args:
        barbeiro_id (int): ID do barbeiro
        
    Returns:
        JSON: Dados do cliente chamado
    """
    try:
        # Verifica se o barbeiro existe
        barbeiro = Barbeiro.query.get_or_404(barbeiro_id)
        
        # Busca o próximo cliente na fila
        proximo_cliente = Cliente.query.filter_by(
            barbeiro_id=barbeiro_id,
            status='aguardando'
        ).order_by(Cliente.data_entrada.asc()).first()
        
        if not proximo_cliente:
            return jsonify({
                'mensagem': 'Não há clientes na fila',
                'status': 'info'
            }), 200
        
        # Marca o cliente como sendo atendido
        proximo_cliente.iniciar_atendimento()
        
        # Salva as alterações
        db.session.commit()
        
        return jsonify({
            'cliente_chamado': proximo_cliente.to_dict(),
            'barbeiro': barbeiro.to_dict(),
            'mensagem': f'Cliente {proximo_cliente.nome} (Ficha {proximo_cliente.numero_ficha}) foi chamado',
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'erro': 'Erro ao chamar próximo cliente',
            'detalhes': str(e),
            'status': 'erro'
        }), 500

@barbeiro_bp.route('/barbeiros/<int:barbeiro_id>/ativar', methods=['PUT'])
def ativar_barbeiro(barbeiro_id):
    """
    Ativa um barbeiro no sistema.
    
    Endpoint: PUT /api/barbeiros/<id>/ativar
    
    Args:
        barbeiro_id (int): ID do barbeiro
        
    Returns:
        JSON: Confirmação da ativação
    """
    try:
        barbeiro = Barbeiro.query.get_or_404(barbeiro_id)
        barbeiro.ativar()
        db.session.commit()
        
        return jsonify({
            'barbeiro': barbeiro.to_dict(),
            'mensagem': f'Barbeiro {barbeiro.nome} foi ativado',
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'erro': 'Erro ao ativar barbeiro',
            'detalhes': str(e),
            'status': 'erro'
        }), 500

@barbeiro_bp.route('/barbeiros/<int:barbeiro_id>/desativar', methods=['PUT'])
def desativar_barbeiro(barbeiro_id):
    """
    Desativa um barbeiro no sistema.
    
    Endpoint: PUT /api/barbeiros/<id>/desativar
    
    Args:
        barbeiro_id (int): ID do barbeiro
        
    Returns:
        JSON: Confirmação da desativação
    """
    try:
        barbeiro = Barbeiro.query.get_or_404(barbeiro_id)
        barbeiro.desativar()
        db.session.commit()
        
        return jsonify({
            'barbeiro': barbeiro.to_dict(),
            'mensagem': f'Barbeiro {barbeiro.nome} foi desativado',
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'erro': 'Erro ao desativar barbeiro',
            'detalhes': str(e),
            'status': 'erro'
        }), 500



@barbeiro_bp.route("/barbeiros/<int:barbeiro_id>", methods=["DELETE"])
def deletar_barbeiro(barbeiro_id):
    """
    Deleta um barbeiro do sistema.
    
    Endpoint: DELETE /api/barbeiros/<id>
    
    Args:
        barbeiro_id (int): ID do barbeiro
        
    Returns:
        JSON: Confirmação da exclusão
    """
    try:
        barbeiro = Barbeiro.query.get_or_404(barbeiro_id)
        
        # Verifica se o barbeiro possui clientes em atendimento ou aguardando
        clientes_ativos = Cliente.query.filter(
            Cliente.barbeiro_id == barbeiro_id,
            Cliente.status.in_(["aguardando", "em_atendimento"])
        ).first()

        if clientes_ativos:
            return jsonify({
                "erro": "Não é possível deletar o barbeiro. Existem clientes aguardando ou em atendimento para este barbeiro.",
                "status": "erro"
            }), 400

        db.session.delete(barbeiro)
        db.session.commit()
        
        return jsonify({
            "mensagem": f"Barbeiro {barbeiro.nome} foi deletado com sucesso.",
            "status": "sucesso"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "erro": "Erro ao deletar barbeiro.",
            "detalhes": str(e),
            "status": "erro"
        }), 500


