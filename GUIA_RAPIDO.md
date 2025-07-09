# 🚀 Guia Rápido - Sistema de Fila Digital

## ⚡ Início Rápido (3 Passos)

### 1️⃣ Abra o Terminal/Prompt
```bash
# Navegue até a pasta do projeto
cd sistema-fila-barbearia
```

### 2️⃣ Execute o Sistema
```bash
# Execute o script de inicialização
./iniciar_sistema.sh
```

### 3️⃣ Acesse no Navegador
- **Sistema Completo:** http://localhost:5000
- **Cadastro:** http://localhost:5000/#cadastro
- **Fila (TV):** http://localhost:5000/#fila

## 📱 Como Usar - Passo a Passo

### 👥 Cadastrar Cliente
1. Clique em **"Cadastro"** no menu
2. Preencha:
   - Nome do cliente
   - Número da ficha
   - Barbeiro preferido
3. Clique **"Cadastrar na Fila"**

### 📺 Visualizar Fila (TV)
1. Clique em **"Fila"** no menu
2. Deixe a tela aberta na TV
3. Atualização automática a cada 5 segundos

### ✂️ Controlar Atendimentos
1. Na seção **"Fila"**
2. Para cada cliente:
   - **▶️ Chamar:** Inicia atendimento
   - **✅ Concluir:** Finaliza atendimento
   - **❌ Cancelar:** Remove da fila

## 🔧 Comandos Úteis

### Iniciar Sistema
```bash
./iniciar_sistema.sh
```

### Parar Sistema
- Pressione **Ctrl+C** no terminal

### Verificar Status
- Acesse: http://localhost:5000/api/status

## 📊 Páginas Principais

| Página | URL | Uso |
|--------|-----|-----|
| **Início** | http://localhost:5000 | Visão geral |
| **Cadastro** | http://localhost:5000/#cadastro | Recepção |
| **Fila** | http://localhost:5000/#fila | TV/Barbeiros |
| **Barbeiros** | http://localhost:5000/#barbeiros | Gerenciamento |
| **Relatórios** | http://localhost:5000/#relatorios | Estatísticas |

## ⚠️ Problemas Comuns

### Sistema não inicia
```bash
# Verifique se está na pasta correta
ls -la
# Deve mostrar: src/, venv/, README.md, etc.
```

### Porta ocupada
```bash
# Mate processos na porta 5000
pkill -f "python src/main.py"
```

### Erro de dependências
```bash
# Reinstale dependências
source venv/bin/activate
pip install -r requirements.txt
```

## 💡 Dicas Importantes

- ✅ **Sempre use o script** `./iniciar_sistema.sh`
- ✅ **Mantenha o terminal aberto** enquanto usa o sistema
- ✅ **Use Chrome/Firefox** para melhor experiência
- ✅ **Backup automático** é criado a cada inicialização
- ✅ **Dados persistem** entre reinicializações

## 📞 Suporte

1. **Leia o README.md** completo
2. **Verifique os logs** no terminal
3. **Teste em navegador diferente**
4. **Reinicie o sistema** se necessário

---

**🔥 Sistema pronto para uso! Boa sorte com sua barbearia! ✂️**

