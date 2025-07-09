# -*- coding: utf-8 -*-
"""
Sistema de Fila Digital para Barbearia
Rotas da API: Atendimentos e Relatórios

Este arquivo contém todas as rotas da API REST relacionadas
ao histórico de atendimentos e geração de relatórios.

ATENÇÃO: Este código é propriedade intelectual protegida.
Uso não autorizado é proibido por lei.
"""

from flask import Blueprint, jsonify, request, send_file
from src.models.user import db
from src.models.atendimento import Atendimento
from src.models.barbeiro import Barbeiro
from datetime import datetime, timedelta
import csv
import io
import os

# Criação do blueprint para as rotas de atendimentos
atendimento_bp = Blueprint('atendimento', __name__)

@atendimento_bp.route('/atendimentos', methods=['GET'])
def listar_atendimentos():
    """
    Lista todos os atendimentos com filtros opcionais.
    
    Endpoint: GET /api/atendimentos
    
    Query Parameters:
        - barbeiro_id: Filtrar por barbeiro
        - data_inicio: Data de início (formato: YYYY-MM-DD)
        - data_fim: Data de fim (formato: YYYY-MM-DD)
        - limite: Número máximo de resultados (padrão: 100)
        - pagina: Página dos resultados (padrão: 1)
    
    Returns:
        JSON: Lista de atendimentos com paginação
    """
    try:
        # Parâmetros de consulta
        barbeiro_id = request.args.get('barbeiro_id', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        limite = request.args.get('limite', 100, type=int)
        pagina = request.args.get('pagina', 1, type=int)
        
        # Construção da query base
        query = Atendimento.query
        
        # Aplicação dos filtros
        if barbeiro_id:
            query = query.filter(Atendimento.barbeiro_id == barbeiro_id)
        
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
                query = query.filter(Atendimento.data_inicio >= data_inicio_obj)
            except ValueError:
                return jsonify({
                    'erro': 'Formato de data_inicio inválido. Use YYYY-MM-DD',
                    'status': 'erro'
                }), 400
        
        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Atendimento.data_inicio < data_fim_obj)
            except ValueError:
                return jsonify({
                    'erro': 'Formato de data_fim inválido. Use YYYY-MM-DD',
                    'status': 'erro'
                }), 400
        
        # Ordenação por data mais recente
        query = query.order_by(Atendimento.data_inicio.desc())
        
        # Paginação
        atendimentos_paginados = query.paginate(
            page=pagina,
            per_page=limite,
            error_out=False
        )
        
        # Conversão para dicionários
        atendimentos_data = [atendimento.to_dict() for atendimento in atendimentos_paginados.items]
        
        return jsonify({
            'atendimentos': atendimentos_data,
            'total': atendimentos_paginados.total,
            'pagina_atual': pagina,
            'total_paginas': atendimentos_paginados.pages,
            'tem_proxima': atendimentos_paginados.has_next,
            'tem_anterior': atendimentos_paginados.has_prev,
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'erro': 'Erro interno do servidor',
            'detalhes': str(e),
            'status': 'erro'
        }), 500

@atendimento_bp.route('/atendimentos/<int:atendimento_id>', methods=['GET'])
def obter_atendimento(atendimento_id):
    """
    Obtém os dados de um atendimento específico.
    
    Endpoint: GET /api/atendimentos/<id>
    
    Args:
        atendimento_id (int): ID do atendimento
        
    Returns:
        JSON: Dados completos do atendimento
    """
    try:
        atendimento = Atendimento.query.get_or_404(atendimento_id)
        barbeiro = Barbeiro.query.get(atendimento.barbeiro_id)
        
        return jsonify({
            'atendimento': atendimento.to_dict(),
            'barbeiro': barbeiro.to_dict() if barbeiro else None,
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'erro': 'Atendimento não encontrado',
            'status': 'erro'
        }), 404

@atendimento_bp.route('/relatorios/estatisticas', methods=['GET'])
def obter_estatisticas():
    """
    Obtém estatísticas gerais dos atendimentos.
    
    Endpoint: GET /api/relatorios/estatisticas
    
    Query Parameters:
        - periodo: Período para análise (hoje, semana, mes, ano)
        - barbeiro_id: Filtrar por barbeiro específico
    
    Returns:
        JSON: Estatísticas detalhadas dos atendimentos
    """
    try:
        periodo = request.args.get('periodo', 'hoje')
        barbeiro_id = request.args.get('barbeiro_id', type=int)
        
        # Definição do período
        agora = datetime.utcnow()
        if periodo == 'hoje':
            data_inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
        elif periodo == 'semana':
            data_inicio = agora - timedelta(days=7)
        elif periodo == 'mes':
            data_inicio = agora - timedelta(days=30)
        elif periodo == 'ano':
            data_inicio = agora - timedelta(days=365)
        else:
            data_inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Query base
        query = Atendimento.query.filter(Atendimento.data_inicio >= data_inicio)
        
        if barbeiro_id:
            query = query.filter(Atendimento.barbeiro_id == barbeiro_id)
        
        atendimentos = query.all()
        
        # Cálculo das estatísticas
        total_atendimentos = len(atendimentos)
        
        if total_atendimentos == 0:
            return jsonify({
                'estatisticas': {
                    'total_atendimentos': 0,
                    'tempo_medio_espera': 0,
                    'tempo_medio_atendimento': 0,
                    'tempo_total_medio': 0
                },
                'periodo': periodo,
                'status': 'sucesso'
            }), 200
        
        # Cálculos de tempo
        tempos_espera = [a.tempo_espera for a in atendimentos if a.tempo_espera is not None]
        tempos_atendimento = [a.tempo_atendimento for a in atendimentos if a.tempo_atendimento is not None]
        
        tempo_medio_espera = sum(tempos_espera) / len(tempos_espera) if tempos_espera else 0
        tempo_medio_atendimento = sum(tempos_atendimento) / len(tempos_atendimento) if tempos_atendimento else 0
        
        # Estatísticas por barbeiro
        estatisticas_barbeiros = {}
        for atendimento in atendimentos:
            barbeiro_id_atual = atendimento.barbeiro_id
            if barbeiro_id_atual not in estatisticas_barbeiros:
                barbeiro = Barbeiro.query.get(barbeiro_id_atual)
                estatisticas_barbeiros[barbeiro_id_atual] = {
                    'nome_barbeiro': barbeiro.nome if barbeiro else 'Desconhecido',
                    'total_atendimentos': 0,
                    'tempo_total_espera': 0,
                    'tempo_total_atendimento': 0
                }
            
            estatisticas_barbeiros[barbeiro_id_atual]['total_atendimentos'] += 1
            if atendimento.tempo_espera:
                estatisticas_barbeiros[barbeiro_id_atual]['tempo_total_espera'] += atendimento.tempo_espera
            if atendimento.tempo_atendimento:
                estatisticas_barbeiros[barbeiro_id_atual]['tempo_total_atendimento'] += atendimento.tempo_atendimento
        
        # Cálculo de médias por barbeiro
        for barbeiro_stats in estatisticas_barbeiros.values():
            total = barbeiro_stats['total_atendimentos']
            barbeiro_stats['tempo_medio_espera'] = barbeiro_stats['tempo_total_espera'] / total if total > 0 else 0
            barbeiro_stats['tempo_medio_atendimento'] = barbeiro_stats['tempo_total_atendimento'] / total if total > 0 else 0
        
        return jsonify({
            'estatisticas': {
                'total_atendimentos': total_atendimentos,
                'tempo_medio_espera': round(tempo_medio_espera, 2),
                'tempo_medio_atendimento': round(tempo_medio_atendimento, 2),
                'tempo_total_medio': round(tempo_medio_espera + tempo_medio_atendimento, 2)
            },
            'estatisticas_por_barbeiro': list(estatisticas_barbeiros.values()),
            'periodo': periodo,
            'data_inicio': data_inicio.isoformat(),
            'data_fim': agora.isoformat(),
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'erro': 'Erro ao calcular estatísticas',
            'detalhes': str(e),
            'status': 'erro'
        }), 500

@atendimento_bp.route('/relatorios/exportar-csv', methods=['GET'])
def exportar_csv():
    """
    Exporta os atendimentos para um arquivo CSV.
    
    Endpoint: GET /api/relatorios/exportar-csv
    
    Query Parameters:
        - barbeiro_id: Filtrar por barbeiro
        - data_inicio: Data de início (formato: YYYY-MM-DD)
        - data_fim: Data de fim (formato: YYYY-MM-DD)
    
    Returns:
        File: Arquivo CSV com os dados dos atendimentos
    """
    try:
        # Parâmetros de consulta
        barbeiro_id = request.args.get('barbeiro_id', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Construção da query
        query = Atendimento.query
        
        if barbeiro_id:
            query = query.filter(Atendimento.barbeiro_id == barbeiro_id)
        
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
                query = query.filter(Atendimento.data_inicio >= data_inicio_obj)
            except ValueError:
                return jsonify({
                    'erro': 'Formato de data_inicio inválido. Use YYYY-MM-DD',
                    'status': 'erro'
                }), 400
        
        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Atendimento.data_inicio < data_fim_obj)
            except ValueError:
                return jsonify({
                    'erro': 'Formato de data_fim inválido. Use YYYY-MM-DD',
                    'status': 'erro'
                }), 400
        
        # Ordenação por data
        atendimentos = query.order_by(Atendimento.data_inicio.desc()).all()
        
        # Criação do arquivo CSV em memória
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho do CSV
        writer.writerow([
            'ID',
            'Número da Ficha',
            'Nome do Cliente',
            'ID do Barbeiro',
            'Nome do Barbeiro',
            'Data de Entrada',
            'Data de Início',
            'Data de Fim',
            'Tempo de Espera (min)',
            'Tempo de Atendimento (min)',
            'Tempo Total (min)'
        ])
        
        # Dados dos atendimentos
        for atendimento in atendimentos:
            barbeiro = Barbeiro.query.get(atendimento.barbeiro_id)
            nome_barbeiro = barbeiro.nome if barbeiro else 'Desconhecido'
            
            writer.writerow([
                atendimento.id,
                atendimento.numero_ficha,
                atendimento.nome_cliente,
                atendimento.barbeiro_id,
                nome_barbeiro,
                atendimento.data_entrada.strftime('%d/%m/%Y %H:%M:%S') if atendimento.data_entrada else '',
                atendimento.data_inicio.strftime('%d/%m/%Y %H:%M:%S') if atendimento.data_inicio else '',
                atendimento.data_fim.strftime('%d/%m/%Y %H:%M:%S') if atendimento.data_fim else '',
                atendimento.tempo_espera or 0,
                atendimento.tempo_atendimento or 0,
                (atendimento.tempo_espera or 0) + (atendimento.tempo_atendimento or 0)
            ])
        
        # Preparação do arquivo para download
        output.seek(0)
        
        # Criação de um arquivo temporário
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f'atendimentos_barbearia_{timestamp}.csv'
        
        # Conversão para bytes
        csv_bytes = io.BytesIO()
        csv_bytes.write(output.getvalue().encode('utf-8-sig'))  # UTF-8 com BOM para Excel
        csv_bytes.seek(0)
        
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=nome_arquivo
        )
        
    except Exception as e:
        return jsonify({
            'erro': 'Erro ao exportar CSV',
            'detalhes': str(e),
            'status': 'erro'
        }), 500

@atendimento_bp.route('/relatorios/resumo-diario', methods=['GET'])
def obter_resumo_diario():
    """
    Obtém um resumo dos atendimentos do dia atual.
    
    Endpoint: GET /api/relatorios/resumo-diario
    
    Returns:
        JSON: Resumo detalhado dos atendimentos do dia
    """
    try:
        # Data de hoje
        hoje = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        amanha = hoje + timedelta(days=1)
        
        # Atendimentos de hoje
        atendimentos_hoje = Atendimento.query.filter(
            Atendimento.data_inicio >= hoje,
            Atendimento.data_inicio < amanha
        ).all()
        
        # Resumo por barbeiro
        resumo_barbeiros = {}
        for atendimento in atendimentos_hoje:
            barbeiro_id = atendimento.barbeiro_id
            if barbeiro_id not in resumo_barbeiros:
                barbeiro = Barbeiro.query.get(barbeiro_id)
                resumo_barbeiros[barbeiro_id] = {
                    'nome_barbeiro': barbeiro.nome if barbeiro else 'Desconhecido',
                    'atendimentos': 0,
                    'tempo_total_trabalho': 0,
                    'primeiro_atendimento': None,
                    'ultimo_atendimento': None
                }
            
            resumo_barbeiros[barbeiro_id]['atendimentos'] += 1
            
            if atendimento.tempo_atendimento:
                resumo_barbeiros[barbeiro_id]['tempo_total_trabalho'] += atendimento.tempo_atendimento
            
            # Primeiro e último atendimento
            if not resumo_barbeiros[barbeiro_id]['primeiro_atendimento'] or \
               atendimento.data_inicio < resumo_barbeiros[barbeiro_id]['primeiro_atendimento']:
                resumo_barbeiros[barbeiro_id]['primeiro_atendimento'] = atendimento.data_inicio
            
            if not resumo_barbeiros[barbeiro_id]['ultimo_atendimento'] or \
               atendimento.data_inicio > resumo_barbeiros[barbeiro_id]['ultimo_atendimento']:
                resumo_barbeiros[barbeiro_id]['ultimo_atendimento'] = atendimento.data_inicio
        
        # Formatação das datas
        for resumo in resumo_barbeiros.values():
            if resumo['primeiro_atendimento']:
                resumo['primeiro_atendimento'] = resumo['primeiro_atendimento'].strftime('%H:%M:%S')
            if resumo['ultimo_atendimento']:
                resumo['ultimo_atendimento'] = resumo['ultimo_atendimento'].strftime('%H:%M:%S')
        
        return jsonify({
            'resumo_diario': {
                'data': hoje.strftime('%d/%m/%Y'),
                'total_atendimentos': len(atendimentos_hoje),
                'resumo_por_barbeiro': list(resumo_barbeiros.values())
            },
            'status': 'sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({
            'erro': 'Erro ao gerar resumo diário',
            'detalhes': str(e),
            'status': 'erro'
        }), 500

