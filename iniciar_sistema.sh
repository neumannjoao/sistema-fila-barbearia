#!/bin/bash

# Sistema de Fila Digital para Barbearia
# Script de Inicialização
# 
# ATENÇÃO: Este código é propriedade intelectual protegida.
# Uso não autorizado é proibido por lei.

echo "============================================================"
echo "🔥 SISTEMA DE FILA DIGITAL PARA BARBEARIA"
echo "============================================================"
echo "📅 Iniciando sistema em: $(date '+%d/%m/%Y %H:%M:%S')"
echo "============================================================"

# Verifica se está no diretório correto
if [ ! -f "src/main.py" ]; then
    echo "❌ ERRO: Execute este script a partir do diretório do projeto!"
    echo "   Navegue até a pasta 'sistema-fila-barbearia' e tente novamente."
    exit 1
fi

# Verifica se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ ERRO: Ambiente virtual não encontrado!"
    echo "   Certifique-se de que o projeto foi configurado corretamente."
    exit 1
fi

# Ativa o ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Verifica se as dependências estão instaladas
echo "📦 Verificando dependências..."
if ! pip show flask > /dev/null 2>&1; then
    echo "⚠️  Instalando dependências..."
    pip install -r requirements.txt
fi

# Verifica se a porta 5000 está disponível
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  AVISO: Porta 5000 já está em uso!"
    echo "   Deseja parar o processo existente? (s/n)"
    read -r resposta
    if [ "$resposta" = "s" ] || [ "$resposta" = "S" ]; then
        echo "🛑 Parando processo existente..."
        pkill -f "python src/main.py"
        sleep 2
    else
        echo "❌ Cancelando inicialização."
        exit 1
    fi
fi

# Cria backup do banco de dados se existir
if [ -f "src/database/app.db" ]; then
    echo "💾 Criando backup do banco de dados..."
    mkdir -p backups
    cp src/database/app.db "backups/app_$(date +%Y%m%d_%H%M%S).db"
fi

echo ""
echo "🚀 Iniciando servidor Flask..."
echo ""
echo "📋 INFORMAÇÕES IMPORTANTES:"
echo "   • URL do Sistema: http://localhost:5000"
echo "   • Para parar: Pressione Ctrl+C"
echo "   • Logs: Visíveis no terminal"
echo ""
echo "🌐 ACESSO AO SISTEMA:"
echo "   • Recepção: http://localhost:5000/#cadastro"
echo "   • TV (Fila): http://localhost:5000/#fila"
echo "   • Barbeiros: http://localhost:5000/#barbeiros"
echo "   • Relatórios: http://localhost:5000/#relatorios"
echo ""
echo "============================================================"

# Inicia o sistema
python src/main.py

echo ""
echo "============================================================"
echo "🛑 Sistema finalizado em: $(date '+%d/%m/%Y %H:%M:%S')"
echo "============================================================"

