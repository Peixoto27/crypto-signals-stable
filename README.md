# API de Sinais de Criptomoedas - Railway Deploy Corrigido

API otimizada com porcentagem de alvo e deploy corrigido para Railway.

## 🔧 **CORREÇÃO APLICADA:**

### **Problema Original:**
- Railway tentava executar `/app/src/main.py`
- Arquivo não estava na pasta `src`
- Erro: "No such file or directory"

### **Solução Implementada:**
- ✅ **main.py na raiz** do projeto
- ✅ **Procfile corrigido:** `web: python main.py`
- ✅ **railway.json atualizado:** `"startCommand": "python main.py"`
- ✅ **Estrutura simplificada** sem pasta src

## 📁 **ESTRUTURA CORRETA:**

```
projeto/
├── main.py              ← Arquivo principal na raiz
├── requirements.txt     ← Dependências
├── Procfile            ← Comando de inicialização
├── railway.json        ← Configuração Railway
└── README.md           ← Documentação
```

## 🚀 **COMO FAZER DEPLOY:**

### **1. GitHub:**
1. Crie um novo repositório
2. Faça upload destes 4 arquivos na raiz:
   - `main.py`
   - `requirements.txt`
   - `Procfile`
   - `railway.json`

### **2. Railway:**
1. Acesse [railway.app](https://railway.app)
2. Clique "New Project"
3. Selecione "Deploy from GitHub repo"
4. Escolha seu repositório
5. Deploy automático!

## ✅ **FUNCIONALIDADES:**

- ✅ **API otimizada** com cache de 5 minutos
- ✅ **Porcentagem de alvo** incluída
- ✅ **6 moedas** analisadas
- ✅ **Dados reais** do CoinGecko
- ✅ **Deploy corrigido** para Railway

## 📡 **ENDPOINTS:**

- `GET /` - Informações da API
- `GET /api/health` - Status de saúde
- `GET /api/signals` - Todos os sinais com porcentagem

## 🎯 **EXEMPLO DE RESPOSTA:**

```json
{
  "signals": [
    {
      "symbol": "BTC",
      "signal": "BUY",
      "target_percentage": 8.0,
      "target_price": 127000.00,
      "current_price": 118000.00,
      "strength": 85,
      "confidence": 77
    }
  ]
}
```

**Deploy corrigido e funcionando! 🚀📊**

