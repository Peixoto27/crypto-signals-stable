# API de Sinais Criptográficos - Railway Deploy

## 🚀 Versão 4.0 - Análise Técnica Real

API Flask otimizada para análise de sinais de criptomoedas com indicadores técnicos baseados em dados históricos reais.

### ✨ Características Principais

- **Análise Técnica Real**: RSI calculado com 30 dias de dados históricos
- **Médias Móveis**: SMA5, SMA10, SMA20 baseadas em dados reais
- **Análise de Tendência**: Identificação automática de tendências (BULLISH/BEARISH/NEUTRAL)
- **Sinais Inteligentes**: STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
- **Cache Otimizado**: 5 minutos para reduzir requisições à API
- **Deploy Railway**: Configurado com Gunicorn para produção

### 🔧 Correções Implementadas

1. **Procfile corrigido**: Agora usa Gunicorn em vez de execução direta
2. **railway.json atualizado**: Comando de start correto
3. **Requirements.txt**: Versões estáveis e python-dotenv adicionado
4. **Código principal**: Análise técnica real implementada

### 📊 Moedas Analisadas

- Bitcoin (BTC)
- Ethereum (ETH)
- BNB (BNB)
- Solana (SOL)
- Cardano (ADA)
- Dogecoin (DOGE)
- Shiba Inu (SHIB)
- Pepe (PEPE)

### 🛠️ Como Fazer Deploy no Railway

1. **Preparar o repositório**:
   ```bash
   git add .
   git commit -m "Deploy corrigido - Gunicorn + análise técnica real"
   git push origin main
   ```

2. **No Railway**:
   - Conecte seu repositório GitHub
   - O Railway detectará automaticamente o Python
   - O deploy será feito usando o Gunicorn (configurado no Procfile)

3. **Verificar funcionamento**:
   - Acesse: `https://seu-projeto.up.railway.app/`
   - Teste os endpoints: `/api/health` e `/api/signals`

### 📡 Endpoints da API

#### GET `/`
Informações gerais da API

#### GET `/api/health`
Status de saúde da aplicação

#### GET `/api/signals`
Todos os sinais de criptomoedas com análise técnica

#### GET `/api/signal/<SYMBOL>`
Sinal específico de uma moeda (ex: `/api/signal/BTC`)

### 📈 Exemplo de Resposta

```json
{
  "signals": [
    {
      "symbol": "BTC",
      "name": "Bitcoin",
      "current_price": 43250.50,
      "change_24h": 2.45,
      "signal": "BUY",
      "strength": 75,
      "confidence": 80,
      "target_percentage": 8.5,
      "target_price": 46927.29,
      "stop_loss": 40597.47,
      "technical_indicators": {
        "rsi": 45.2,
        "sma5": 42800.00,
        "sma10": 42100.00,
        "sma20": 41500.00,
        "volatility": 12.5,
        "trend": "BULLISH"
      },
      "reasons": [
        "RSI em zona de compra",
        "Tendência de alta confirmada",
        "Momentum positivo (+2.45%)"
      ],
      "analysis_type": "REAL_DATA"
    }
  ],
  "total_signals": 8,
  "signal_distribution": {
    "BUY": 3,
    "HOLD": 4,
    "SELL": 1
  }
}
```

### 🔍 Indicadores Técnicos

- **RSI**: Índice de Força Relativa (14 períodos)
- **SMA5/10/20**: Médias móveis simples
- **Volatilidade**: Desvio padrão dos últimos 7 dias
- **Tendência**: Análise baseada na posição das médias móveis

### ⚡ Otimizações

- Cache de 5 minutos para reduzir requisições
- Uma única requisição para buscar todos os preços
- Dados históricos em cache separado
- Análise técnica baseada em dados reais da CoinGecko

### 🚨 Importante

- A API usa dados gratuitos da CoinGecko
- Limite de requisições respeitado com cache inteligente
- Sinais são para fins educacionais, não constituem aconselhamento financeiro

### 📝 Logs

A aplicação gera logs detalhados para monitoramento:
- Requisições à API externa
- Cache hits/misses
- Erros de análise técnica
- Performance dos endpoints

---

**Versão**: 4.0  
**Deploy**: Railway + Gunicorn  
**Status**: ✅ Funcionando

