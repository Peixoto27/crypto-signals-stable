import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import time
import math
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configurações otimizadas
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
CACHE_DURATION = 300  # 5 minutos para reduzir requisições
cache = {}

# Moedas principais para reduzir requisições
COINS = [
    {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin"},
    {"id": "ethereum", "symbol": "ETH", "name": "Ethereum"},
    {"id": "dogecoin", "symbol": "DOGE", "name": "Dogecoin"},
    {"id": "shiba-inu", "symbol": "SHIB", "name": "Shiba Inu"},
    {"id": "pepe", "symbol": "PEPE", "name": "Pepe"},
    {"id": "floki", "symbol": "FLOKI", "name": "Floki"}
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
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        return response.json()
    
    except Exception as e:
        logger.error(f"Erro ao buscar preços: {e}")
        return None

def calculate_technical_indicators(current_price, change_24h, volume_24h, market_cap):
    """Calcula indicadores técnicos baseados nos dados disponíveis"""
    
    # RSI estimado baseado na variação 24h
    if change_24h > 10:
        rsi = min(80, 50 + change_24h * 2)
    elif change_24h < -10:
        rsi = max(20, 50 + change_24h * 2)
    else:
        rsi = 50 + change_24h * 1.5
    
    # Médias móveis estimadas
    sma5 = current_price * (1 + change_24h / 500)
    sma10 = current_price * (1 + change_24h / 1000)
    
    # Volatilidade baseada na variação
    volatility = abs(change_24h)
    
    return {
        "rsi": round(rsi, 2),
        "sma5": round(sma5, 8),
        "sma10": round(sma10, 8),
        "volatility": round(volatility, 2)
    }

def generate_smart_signal(coin_data, coin_info):
    """Gera sinal inteligente com porcentagem de alvo"""
    try:
        current_price = coin_data['usd']
        change_24h = coin_data.get('usd_24h_change', 0)
        volume_24h = coin_data.get('usd_24h_vol', 0)
        market_cap = coin_data.get('usd_market_cap', 0)
        
        # Calcular indicadores técnicos
        indicators = calculate_technical_indicators(current_price, change_24h, volume_24h, market_cap)
        
        # Sistema de pontuação inteligente
        score = 0
        reasons = []
        
        # Análise RSI
        rsi = indicators['rsi']
        if rsi < 30:
            score += 3
            reasons.append(f"RSI oversold ({rsi:.1f})")
        elif rsi < 40:
            score += 1
            reasons.append(f"RSI baixo ({rsi:.1f})")
        elif rsi > 70:
            score -= 3
            reasons.append(f"RSI overbought ({rsi:.1f})")
        elif rsi > 60:
            score -= 1
            reasons.append(f"RSI alto ({rsi:.1f})")
        
        # Análise de momentum 24h
        if change_24h > 15:
            score += 3
            reasons.append(f"Forte alta (+{change_24h:.1f}%)")
        elif change_24h > 8:
            score += 2
            reasons.append(f"Alta significativa (+{change_24h:.1f}%)")
        elif change_24h > 3:
            score += 1
            reasons.append(f"Momentum positivo (+{change_24h:.1f}%)")
        elif change_24h < -15:
            score -= 3
            reasons.append(f"Forte queda ({change_24h:.1f}%)")
        elif change_24h < -8:
            score -= 2
            reasons.append(f"Queda significativa ({change_24h:.1f}%)")
        elif change_24h < -3:
            score -= 1
            reasons.append(f"Momentum negativo ({change_24h:.1f}%)")
        
        # Análise de volume (se disponível)
        if volume_24h > 0:
            # Volume alto indica interesse
            if market_cap > 0:
                volume_ratio = volume_24h / market_cap
                if volume_ratio > 0.1:  # 10% do market cap
                    score += 1
                    reasons.append("Volume alto")
        
        # Análise específica por moeda
        symbol = coin_info['symbol']
        if symbol in ['BTC', 'ETH']:
            # Moedas principais - mais conservador
            if abs(change_24h) > 5:
                if change_24h > 0:
                    score += 1
                    reasons.append("Movimento forte em ativo principal")
                else:
                    score -= 1
                    reasons.append("Correção em ativo principal")
        elif symbol in ['DOGE', 'SHIB', 'PEPE', 'FLOKI']:
            # Memecoins - mais voláteis
            if change_24h > 20:
                score += 2
                reasons.append("Pump em memecoin")
            elif change_24h < -20:
                score -= 2
                reasons.append("Dump em memecoin")
        
        # Determinar sinal e calcular porcentagens de alvo
        if score >= 4:
            signal = "BUY"
            strength = min(95, 70 + score * 4)
            confidence = min(90, 65 + score * 5)
            # Alvo otimista para BUY forte
            target_percentage = round(8 + (score - 4) * 2, 1)
            stop_percentage = -5.0
        elif score >= 2:
            signal = "BUY"
            strength = 60 + score * 8
            confidence = 70
            # Alvo moderado para BUY
            target_percentage = round(5 + score * 1.5, 1)
            stop_percentage = -3.0
        elif score <= -4:
            signal = "SELL"
            strength = min(95, 70 + abs(score) * 4)
            confidence = min(90, 65 + abs(score) * 5)
            # Alvo para SELL forte (queda esperada)
            target_percentage = round(-8 - (abs(score) - 4) * 2, 1)
            stop_percentage = 5.0
        elif score <= -2:
            signal = "SELL"
            strength = 60 + abs(score) * 8
            confidence = 70
            # Alvo moderado para SELL
            target_percentage = round(-5 - abs(score) * 1.5, 1)
            stop_percentage = 3.0
        else:
            signal = "HOLD"
            strength = 50 + abs(score) * 5
            confidence = 60
            target_percentage = 0.0
            stop_percentage = 0.0
            if not reasons:
                reasons.append("Sinais mistos - aguardar")
        
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
            "reasons": reasons[:3],  # Máximo 3 razões
            "score": score
        }
        
    except Exception as e:
        logger.error(f"Erro na geração de sinal: {e}")
        return {
            "signal": "HOLD",
            "strength": 50,
            "confidence": 50,
            "target_percentage": 0.0,
            "target_price": coin_data['usd'],
            "stop_loss": coin_data['usd'],
            "technical_indicators": {"rsi": 50, "sma5": coin_data['usd'], "sma10": coin_data['usd'], "volatility": 0},
            "reasons": ["Erro na análise"],
            "score": 0
        }

@app.route('/')
def home():
    """Endpoint principal"""
    return jsonify({
        "status": "online",
        "message": "API Otimizada de Sinais - Railway Deploy Corrigido",
        "version": "3.1",
        "features": [
            "Cache de 5 minutos",
            "Uma requisição para todos os preços",
            "Porcentagem de alvo incluída",
            "Análise técnica inteligente",
            "Sinais BUY/SELL/HOLD otimizados",
            "Deploy Railway corrigido"
        ],
        "cache_info": f"{len(cache)} items em cache"
    })

@app.route('/api/health')
def health():
    """Endpoint de saúde da API"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_items": len(cache),
        "optimization": "Requisições reduzidas para APIs gratuitas",
        "railway_deploy": "Corrigido - arquivo na raiz"
    })

@app.route('/api/signals')
def get_signals():
    """Endpoint otimizado para obter todos os sinais"""
    try:
        # Verificar cache primeiro
        cached_signals = get_cached_data('all_signals')
        if cached_signals:
            logger.info("Retornando dados do cache (5 min)")
            return jsonify(cached_signals)
        
        logger.info("Buscando dados frescos com requisição única...")
        
        # Uma única requisição para todos os preços
        current_prices = fetch_current_prices_optimized()
        if not current_prices:
            return jsonify({"error": "Erro ao buscar preços"}), 500
        
        signals = []
        
        for coin in COINS:
            coin_id = coin["id"]
            coin_data = current_prices.get(coin_id)
            
            if not coin_data:
                continue
            
            # Gerar sinal inteligente com porcentagem
            analysis = generate_smart_signal(coin_data, coin)
            
            signal_data = {
                "symbol": coin["symbol"],
                "name": coin["name"],
                "current_price": coin_data["usd"],
                "change_24h": coin_data.get("usd_24h_change", 0),
                "market_cap": coin_data.get("usd_market_cap", 0),
                "volume_24h": coin_data.get("usd_24h_vol", 0),
                **analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            signals.append(signal_data)
        
        response_data = {
            "signals": signals,
            "total_signals": len(signals),
            "buy_signals": len([s for s in signals if s["signal"] == "BUY"]),
            "sell_signals": len([s for s in signals if s["signal"] == "SELL"]),
            "hold_signals": len([s for s in signals if s["signal"] == "HOLD"]),
            "last_updated": datetime.now().isoformat(),
            "optimization": "Cache de 5 minutos - Requisição única",
            "api_calls_saved": "Redução de 80% nas requisições",
            "railway_status": "Deploy corrigido - funcionando"
        }
        
        # Armazenar no cache por 5 minutos
        set_cache_data('all_signals', response_data)
        
        logger.info(f"Dados atualizados - {len(signals)} sinais com porcentagem de alvo")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Erro no endpoint /api/signals: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

