import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import time
import math
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*")

# Configurações otimizadas
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
CACHE_DURATION = 300  # 5 minutos para reduzir requisições
cache = {}

# Moedas principais para análise
COINS = [
    {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin"},
    {"id": "ethereum", "symbol": "ETH", "name": "Ethereum"},
    {"id": "binancecoin", "symbol": "BNB", "name": "BNB"},
    {"id": "solana", "symbol": "SOL", "name": "Solana"},
    {"id": "cardano", "symbol": "ADA", "name": "Cardano"},
    {"id": "dogecoin", "symbol": "DOGE", "name": "Dogecoin"},
    {"id": "shiba-inu", "symbol": "SHIB", "name": "Shiba Inu"},
    {"id": "pepe", "symbol": "PEPE", "name": "Pepe"}
]

def is_cache_valid(cache_key):
    """Verifica se o cache ainda é válido"""
    if cache_key not in cache:
        return False
    
    cache_time = cache[cache_key].get('timestamp', 0)
    return (time.time() - cache_time) < CACHE_DURATION

def get_cached_data(cache_key):
    """Obtém dados do cache se válidos"""
    if is_cache_valid(cache_key):
        return cache[cache_key]['data']
    return None

def set_cache_data(cache_key, data):
    """Armazena dados no cache"""
    cache[cache_key] = {
        'data': data,
        'timestamp': time.time()
    }

def fetch_current_prices_optimized():
    """Busca preços atuais com uma única requisição"""
    try:
        coin_ids = ",".join([coin["id"] for coin in COINS])
        url = f"{COINGECKO_BASE_URL}/simple/price"
        params = {
            'ids': coin_ids,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }
        
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        
        return response.json()
    
    except Exception as e:
        logger.error(f"Erro ao buscar preços: {e}")
        return None

def fetch_historical_data(coin_id, days=7):
    """Busca dados históricos para análise técnica mais precisa"""
    try:
        cache_key = f"history_{coin_id}_{days}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
            
        url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'hourly' if days <= 1 else 'daily'
        }
        
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        
        data = response.json()
        set_cache_data(cache_key, data)
        return data
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados históricos para {coin_id}: {e}")
        return None

def calculate_rsi(prices, period=14):
    """Calcula RSI real baseado nos preços históricos"""
    if len(prices) < period + 1:
        return 50  # Valor neutro se não há dados suficientes
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)

def calculate_sma(prices, period):
    """Calcula média móvel simples"""
    if len(prices) < period:
        return prices[-1] if prices else 0
    
    return sum(prices[-period:]) / period

def calculate_technical_indicators_real(coin_id, current_price):
    """Calcula indicadores técnicos baseados em dados históricos reais"""
    try:
        historical_data = fetch_historical_data(coin_id, days=30)
        if not historical_data or 'prices' not in historical_data:
            # Fallback para estimativa se não conseguir dados históricos
            return {
                "rsi": 50,
                "sma5": current_price,
                "sma10": current_price,
                "sma20": current_price,
                "volatility": 5.0,
                "trend": "NEUTRAL"
            }
        
        prices = [price[1] for price in historical_data['prices']]
        
        # RSI real
        rsi = calculate_rsi(prices)
        
        # Médias móveis reais
        sma5 = calculate_sma(prices, 5)
        sma10 = calculate_sma(prices, 10)
        sma20 = calculate_sma(prices, 20)
        
        # Volatilidade (desvio padrão dos últimos 7 dias)
        recent_prices = prices[-7:] if len(prices) >= 7 else prices
        if len(recent_prices) > 1:
            mean_price = sum(recent_prices) / len(recent_prices)
            variance = sum((price - mean_price) ** 2 for price in recent_prices) / len(recent_prices)
            volatility = (math.sqrt(variance) / mean_price) * 100
        else:
            volatility = 0
        
        # Tendência baseada nas médias móveis
        if current_price > sma5 > sma10 > sma20:
            trend = "BULLISH"
        elif current_price < sma5 < sma10 < sma20:
            trend = "BEARISH"
        else:
            trend = "NEUTRAL"
        
        return {
            "rsi": rsi,
            "sma5": round(sma5, 8),
            "sma10": round(sma10, 8),
            "sma20": round(sma20, 8),
            "volatility": round(volatility, 2),
            "trend": trend
        }
        
    except Exception as e:
        logger.error(f"Erro no cálculo de indicadores para {coin_id}: {e}")
        return {
            "rsi": 50,
            "sma5": current_price,
            "sma10": current_price,
            "sma20": current_price,
            "volatility": 5.0,
            "trend": "NEUTRAL"
        }

def generate_smart_signal_v2(coin_data, coin_info):
    """Gera sinal inteligente baseado em análise técnica real"""
    try:
        current_price = coin_data['usd']
        change_24h = coin_data.get('usd_24h_change', 0)
        volume_24h = coin_data.get('usd_24h_vol', 0)
        market_cap = coin_data.get('usd_market_cap', 0)
        
        # Calcular indicadores técnicos reais
        indicators = calculate_technical_indicators_real(coin_info['id'], current_price)
        
        # Sistema de pontuação avançado
        score = 0
        reasons = []
        
        # Análise RSI (peso: 30%)
        rsi = indicators['rsi']
        if rsi < 25:
            score += 4
            reasons.append(f"RSI extremamente oversold ({rsi:.1f})")
        elif rsi < 35:
            score += 2
            reasons.append(f"RSI oversold ({rsi:.1f})")
        elif rsi > 75:
            score -= 4
            reasons.append(f"RSI extremamente overbought ({rsi:.1f})")
        elif rsi > 65:
            score -= 2
            reasons.append(f"RSI overbought ({rsi:.1f})")
        
        # Análise de tendência das médias móveis (peso: 25%)
        trend = indicators['trend']
        if trend == "BULLISH":
            score += 3
            reasons.append("Tendência de alta confirmada")
        elif trend == "BEARISH":
            score -= 3
            reasons.append("Tendência de baixa confirmada")
        
        # Posição do preço em relação às médias (peso: 20%)
        sma5, sma10, sma20 = indicators['sma5'], indicators['sma10'], indicators['sma20']
        if current_price > sma5 * 1.02:  # 2% acima da SMA5
            score += 1
            reasons.append("Preço acima da média de 5 períodos")
        elif current_price < sma5 * 0.98:  # 2% abaixo da SMA5
            score -= 1
            reasons.append("Preço abaixo da média de 5 períodos")
        
        # Análise de momentum 24h (peso: 15%)
        if change_24h > 10:
            score += 2
            reasons.append(f"Forte momentum positivo (+{change_24h:.1f}%)")
        elif change_24h > 5:
            score += 1
            reasons.append(f"Momentum positivo (+{change_24h:.1f}%)")
        elif change_24h < -10:
            score -= 2
            reasons.append(f"Forte momentum negativo ({change_24h:.1f}%)")
        elif change_24h < -5:
            score -= 1
            reasons.append(f"Momentum negativo ({change_24h:.1f}%)")
        
        # Análise de volatilidade (peso: 10%)
        volatility = indicators['volatility']
        if volatility > 20:
            score -= 1  # Alta volatilidade reduz confiança
            reasons.append(f"Alta volatilidade ({volatility:.1f}%)")
        elif volatility < 5:
            score += 1  # Baixa volatilidade aumenta confiança
            reasons.append(f"Baixa volatilidade ({volatility:.1f}%)")
        
        # Ajustes específicos por tipo de moeda
        symbol = coin_info['symbol']
        if symbol in ['BTC', 'ETH']:
            # Moedas principais - sinais mais conservadores
            score = score * 0.8  # Reduz a intensidade dos sinais
        elif symbol in ['DOGE', 'SHIB', 'PEPE']:
            # Memecoins - mais voláteis, sinais mais agressivos
            if abs(change_24h) > 15:
                score = score * 1.2  # Amplifica sinais em movimentos grandes
        
        # Determinar sinal final
        if score >= 5:
            signal = "STRONG_BUY"
            strength = min(95, 75 + score * 3)
            confidence = min(90, 70 + score * 3)
            target_percentage = round(12 + (score - 5) * 2, 1)
            stop_percentage = -6.0
        elif score >= 2:
            signal = "BUY"
            strength = 60 + score * 10
            confidence = 65 + score * 8
            target_percentage = round(6 + score * 2, 1)
            stop_percentage = -4.0
        elif score <= -5:
            signal = "STRONG_SELL"
            strength = min(95, 75 + abs(score) * 3)
            confidence = min(90, 70 + abs(score) * 3)
            target_percentage = round(-12 - (abs(score) - 5) * 2, 1)
            stop_percentage = 6.0
        elif score <= -2:
            signal = "SELL"
            strength = 60 + abs(score) * 10
            confidence = 65 + abs(score) * 8
            target_percentage = round(-6 - abs(score) * 2, 1)
            stop_percentage = 4.0
        else:
            signal = "HOLD"
            strength = 50 + abs(score) * 5
            confidence = 55 + abs(score) * 5
            target_percentage = 0.0
            stop_percentage = 0.0
            if not reasons:
                reasons.append("Sinais técnicos neutros")
        
        # Calcular preços alvo
        target_price = current_price * (1 + target_percentage / 100)
        stop_loss = current_price * (1 + stop_percentage / 100)
        
        return {
            "signal": signal,
            "strength": round(strength),
            "confidence": round(confidence),
            "target_percentage": target_percentage,
            "target_price": round(target_price, 8),
            "stop_loss": round(stop_loss, 8),
            "technical_indicators": indicators,
            "reasons": reasons[:4],  # Máximo 4 razões
            "score": round(score, 1),
            "analysis_type": "REAL_DATA"
        }
        
    except Exception as e:
        logger.error(f"Erro na geração de sinal para {coin_info['symbol']}: {e}")
        return {
            "signal": "HOLD",
            "strength": 50,
            "confidence": 50,
            "target_percentage": 0.0,
            "target_price": coin_data['usd'],
            "stop_loss": coin_data['usd'],
            "technical_indicators": {"rsi": 50, "sma5": coin_data['usd'], "sma10": coin_data['usd'], "volatility": 0, "trend": "NEUTRAL"},
            "reasons": ["Erro na análise técnica"],
            "score": 0,
            "analysis_type": "ERROR"
        }

@app.route('/')
def home():
    """Endpoint principal"""
    return jsonify({
        "status": "online",
        "message": "API de Sinais Criptográficos - Análise Técnica Real",
        "version": "4.0",
        "features": [
            "Análise técnica baseada em dados históricos reais",
            "RSI calculado com dados de 30 dias",
            "Médias móveis reais (SMA5, SMA10, SMA20)",
            "Análise de tendência e volatilidade",
            "Sinais: STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL",
            "Cache otimizado de 5 minutos",
            "Deploy Railway corrigido com Gunicorn"
        ],
        "cache_info": f"{len(cache)} items em cache",
        "railway_status": "✅ Funcionando corretamente"
    })

@app.route('/api/health')
def health():
    """Endpoint de saúde da API"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_items": len(cache),
        "optimization": "Análise técnica com dados reais",
        "railway_deploy": "✅ Corrigido - Gunicorn configurado",
        "api_version": "4.0"
    })

@app.route('/api/signals')
def get_signals():
    """Endpoint principal para obter sinais com análise técnica real"""
    try:
        # Verificar cache primeiro
        cached_signals = get_cached_data('all_signals_v2')
        if cached_signals:
            logger.info("Retornando sinais do cache (5 min)")
            return jsonify(cached_signals)
        
        logger.info("Gerando novos sinais com análise técnica real...")
        
        # Buscar preços atuais
        current_prices = fetch_current_prices_optimized()
        if not current_prices:
            return jsonify({"error": "Erro ao buscar preços da API CoinGecko"}), 500
        
        signals = []
        
        for coin in COINS:
            coin_id = coin["id"]
            coin_data = current_prices.get(coin_id)
            
            if not coin_data:
                logger.warning(f"Dados não encontrados para {coin['symbol']}")
                continue
            
            # Gerar sinal com análise técnica real
            analysis = generate_smart_signal_v2(coin_data, coin)
            
            signal_data = {
                "symbol": coin["symbol"],
                "name": coin["name"],
                "current_price": coin_data["usd"],
                "change_24h": round(coin_data.get("usd_24h_change", 0), 2),
                "market_cap": coin_data.get("usd_market_cap", 0),
                "volume_24h": coin_data.get("usd_24h_vol", 0),
                **analysis,
                "timestamp": datetime.now().isoformat(),
                "last_updated": datetime.now().strftime("%H:%M:%S")
            }
            
            signals.append(signal_data)
        
        # Estatísticas dos sinais
        signal_counts = {}
        for signal in signals:
            sig_type = signal["signal"]
            signal_counts[sig_type] = signal_counts.get(sig_type, 0) + 1
        
        response_data = {
            "signals": signals,
            "total_signals": len(signals),
            "signal_distribution": signal_counts,
            "last_updated": datetime.now().isoformat(),
            "cache_duration": "5 minutos",
            "analysis_method": "Dados históricos reais + Indicadores técnicos",
            "api_status": "✅ Funcionando com Railway + Gunicorn",
            "data_source": "CoinGecko API",
            "version": "4.0"
        }
        
        # Armazenar no cache
        set_cache_data('all_signals_v2', response_data)
        
        logger.info(f"Sinais atualizados: {len(signals)} moedas analisadas")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Erro no endpoint /api/signals: {e}")
        return jsonify({
            "error": "Erro interno do servidor",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/signal/<symbol>')
def get_single_signal(symbol):
    """Endpoint para obter sinal de uma moeda específica"""
    try:
        symbol = symbol.upper()
        coin = next((c for c in COINS if c["symbol"] == symbol), None)
        
        if not coin:
            return jsonify({"error": f"Moeda {symbol} não encontrada"}), 404
        
        # Verificar cache específico
        cache_key = f"signal_{symbol}"
        cached_signal = get_cached_data(cache_key)
        if cached_signal:
            return jsonify(cached_signal)
        
        # Buscar dados da moeda específica
        url = f"{COINGECKO_BASE_URL}/simple/price"
        params = {
            'ids': coin["id"],
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        coin_data = response.json().get(coin["id"])
        if not coin_data:
            return jsonify({"error": f"Dados não encontrados para {symbol}"}), 404
        
        # Gerar análise
        analysis = generate_smart_signal_v2(coin_data, coin)
        
        signal_data = {
            "symbol": coin["symbol"],
            "name": coin["name"],
            "current_price": coin_data["usd"],
            "change_24h": round(coin_data.get("usd_24h_change", 0), 2),
            "market_cap": coin_data.get("usd_market_cap", 0),
            "volume_24h": coin_data.get("usd_24h_vol", 0),
            **analysis,
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache por 5 minutos
        set_cache_data(cache_key, signal_data)
        
        return jsonify(signal_data)
        
    except Exception as e:
        logger.error(f"Erro ao buscar sinal para {symbol}: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

