"""
Sistema de Sinais Crypto - DADOS REAIS SIMPLIFICADO
Versão 4.1 - Sem dependências pesadas
"""

import requests
import time
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify
from flask_cors import CORS
import threading
import math

app = Flask(__name__)
CORS(app)

# Configurações
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Meme coins focadas (preferência do usuário)
CRYPTO_SYMBOLS = {
    'DOGE': 'dogecoin',
    'FLOKI': 'floki',
    'PEPE': 'pepe',
    'BONK': 'bonk',
    'SHIB': 'shiba-inu',
    # Principais para contexto
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'BNB': 'binancecoin'
}

# Armazenamento global
current_signals = []
signal_history = []
market_data_cache = {}
last_update = None

class SimpleDataCollector:
    """Coleta dados reais de forma simplificada"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoSignals/4.1'
        })
    
    def get_real_price_data(self, symbols):
        """Obtém dados reais de preços do CoinGecko"""
        try:
            # Converter símbolos para IDs do CoinGecko
            coin_ids = [CRYPTO_SYMBOLS[symbol] for symbol in symbols if symbol in CRYPTO_SYMBOLS]
            ids_str = ','.join(coin_ids)
            
            # Buscar dados atuais
            url = f"{COINGECKO_API}/simple/price"
            params = {
                'ids': ids_str,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Erro ao buscar preços reais: {e}")
            return {}
    
    def get_historical_prices(self, coin_id, days=1):
        """Obtém preços históricos simplificados"""
        try:
            url = f"{COINGECKO_API}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': '5m'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            prices = [point[1] for point in data['prices']]
            
            return prices
            
        except Exception as e:
            print(f"Erro ao buscar histórico para {coin_id}: {e}")
            return []

class SimpleTechnicalAnalyzer:
    """Calcula indicadores técnicos de forma simples"""
    
    @staticmethod
    def calculate_simple_rsi(prices, period=14):
        """Calcula RSI simplificado"""
        if len(prices) < period + 1:
            return 50
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return 50
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    @staticmethod
    def calculate_simple_macd(prices, fast=12, slow=26):
        """Calcula MACD simplificado"""
        if len(prices) < slow:
            return 0
        
        # EMA simplificada
        def simple_ema(data, period):
            if len(data) < period:
                return data[-1] if data else 0
            
            multiplier = 2 / (period + 1)
            ema = data[0]
            
            for price in data[1:]:
                ema = (price * multiplier) + (ema * (1 - multiplier))
            
            return ema
        
        ema_fast = simple_ema(prices, fast)
        ema_slow = simple_ema(prices, slow)
        
        macd = ema_fast - ema_slow
        
        return round(macd, 4)
    
    @staticmethod
    def calculate_simple_bollinger(prices, period=20):
        """Calcula Bandas de Bollinger simplificadas"""
        if len(prices) < period:
            current_price = prices[-1] if prices else 0
            return current_price * 1.02, current_price * 0.98, current_price
        
        recent_prices = prices[-period:]
        sma = sum(recent_prices) / len(recent_prices)
        
        # Desvio padrão simplificado
        variance = sum((price - sma) ** 2 for price in recent_prices) / len(recent_prices)
        std_dev = math.sqrt(variance)
        
        upper_band = sma + (std_dev * 2)
        lower_band = sma - (std_dev * 2)
        
        return round(upper_band, 6), round(lower_band, 6), round(sma, 6)

class SimpleSignalAnalyzer:
    """Analisa sinais com dados reais de forma simples"""
    
    def __init__(self):
        self.data_collector = SimpleDataCollector()
        self.analyzer = SimpleTechnicalAnalyzer()
        self.min_confidence = 65
    
    def analyze_real_signal(self, symbol):
        """Analisa sinal com dados 100% reais"""
        try:
            # Obter dados históricos reais
            coin_id = CRYPTO_SYMBOLS.get(symbol)
            if not coin_id:
                return None
            
            # Buscar preços históricos
            prices = self.data_collector.get_historical_prices(coin_id)
            if not prices or len(prices) < 30:
                print(f"Dados insuficientes para {symbol}")
                return None
            
            current_price = prices[-1]
            
            # Calcular indicadores reais
            rsi = self.analyzer.calculate_simple_rsi(prices)
            macd = self.analyzer.calculate_simple_macd(prices)
            bb_upper, bb_lower, bb_middle = self.analyzer.calculate_simple_bollinger(prices)
            
            # Sistema de pontuação baseado em indicadores reais
            score = 0
            
            # RSI (30/70 são níveis clássicos)
            if rsi < 30:
                score += 3  # Oversold forte = compra
            elif rsi < 40:
                score += 2  # Oversold = compra
            elif rsi > 70:
                score -= 3  # Overbought forte = venda
            elif rsi > 60:
                score -= 2  # Overbought = venda
            
            # MACD
            if macd > 0.001:
                score += 2  # Momentum positivo forte
            elif macd > 0:
                score += 1  # Momentum positivo
            elif macd < -0.001:
                score -= 2  # Momentum negativo forte
            else:
                score -= 1  # Momentum negativo
            
            # Bollinger Bands
            if current_price <= bb_lower:
                score += 3  # Preço na banda inferior = compra forte
            elif current_price < bb_middle:
                score += 1  # Abaixo da média = compra
            elif current_price >= bb_upper:
                score -= 3  # Preço na banda superior = venda forte
            else:
                score -= 1  # Acima da média = venda
            
            # Tendência de preço (últimos 10 períodos)
            if len(prices) >= 10:
                recent_trend = (prices[-1] - prices[-10]) / prices[-10] * 100
                if recent_trend > 2:
                    score += 1  # Tendência de alta
                elif recent_trend < -2:
                    score -= 1  # Tendência de baixa
            
            # Determinar sinal (critério rigoroso para dados reais)
            if score >= 4:
                signal_type = 'BUY'
                confidence = min(65 + (score * 3), 95)
            elif score <= -4:
                signal_type = 'SELL'
                confidence = min(65 + (abs(score) * 3), 95)
            else:
                return None  # Sinal não forte o suficiente
            
            # Calcular preço alvo baseado na volatilidade real
            if len(prices) >= 20:
                price_changes = []
                for i in range(1, min(21, len(prices))):
                    change = abs(prices[-i] - prices[-i-1]) / prices[-i-1] * 100
                    price_changes.append(change)
                
                avg_volatility = sum(price_changes) / len(price_changes)
                target_percentage = min(max(avg_volatility * 0.8, 2.0), 8.0)  # Entre 2% e 8%
            else:
                target_percentage = 3.0  # Padrão conservador
            
            if signal_type == 'BUY':
                target_price = current_price * (1 + target_percentage / 100)
                target_pct = target_percentage
            else:
                target_price = current_price * (1 - target_percentage / 100)
                target_pct = -target_percentage
            
            return {
                'symbol': symbol,
                'type': signal_type,
                'confidence': round(confidence, 1),
                'price': round(current_price, 6),
                'target_price': round(target_price, 6),
                'target_percentage': round(target_pct, 1),
                'timestamp': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(minutes=30)).isoformat(),
                'indicators': {
                    'rsi': rsi,
                    'macd': macd,
                    'bb_upper': bb_upper,
                    'bb_lower': bb_lower,
                    'bb_middle': bb_middle,
                    'score': score
                },
                'data_source': 'coingecko_real',
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Erro ao analisar {symbol}: {e}")
            return None

# Instância global
signal_analyzer = SimpleSignalAnalyzer()

def update_market_data():
    """Atualiza dados de mercado em background"""
    global current_signals, last_update
    
    while True:
        try:
            print(f"[{datetime.now()}] Atualizando dados reais...")
            
            # Limpar sinais expirados
            now = datetime.now()
            current_signals = [
                signal for signal in current_signals 
                if datetime.fromisoformat(signal['expires_at'].replace('Z', '')) > now
            ]
            
            # Analisar cada moeda com dados reais
            new_signals = []
            for symbol in CRYPTO_SYMBOLS.keys():
                try:
                    signal = signal_analyzer.analyze_real_signal(symbol)
                    if signal:
                        # Verificar se já existe sinal similar
                        existing = next((s for s in current_signals if s['symbol'] == symbol), None)
                        if not existing or existing['type'] != signal['type']:
                            new_signals.append(signal)
                            
                            # Adicionar ao histórico
                            signal_history.append({
                                **signal,
                                'result': 'pending',
                                'created_at': datetime.now().isoformat()
                            })
                    
                    # Delay entre análises para não sobrecarregar API
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Erro ao analisar {symbol}: {e}")
                    continue
            
            # Atualizar sinais atuais
            for new_signal in new_signals:
                # Remover sinal antigo da mesma moeda
                current_signals = [s for s in current_signals if s['symbol'] != new_signal['symbol']]
                current_signals.append(new_signal)
            
            # Manter apenas últimos 50 no histórico
            if len(signal_history) > 50:
                signal_history[:] = signal_history[-50:]
            
            last_update = datetime.now()
            print(f"Atualização concluída. Sinais ativos: {len(current_signals)}")
            
        except Exception as e:
            print(f"Erro na atualização: {e}")
        
        # Aguardar 3 minutos antes da próxima atualização
        time.sleep(180)

# Iniciar thread de atualização
update_thread = threading.Thread(target=update_market_data, daemon=True)
update_thread.start()

# Rotas da API
@app.route('/')
def home():
    return jsonify({
        'message': 'Sistema de sinais crypto com dados 100% reais - Simplificado',
        'status': 'online',
        'system': 'Crypto Signals v4.1 - Real Data Simplified',
        'data_source': 'CoinGecko API',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/signals')
def get_signals():
    return jsonify({
        'signals': current_signals,
        'count': len(current_signals),
        'last_update': last_update.isoformat() if last_update else None,
        'data_source': 'coingecko_real',
        'status': 'active',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'system': 'Crypto Signals v4.1',
        'data_source': 'Real APIs - Simplified',
        'components': {
            'api': True,
            'data_collector': True,
            'signal_analyzer': True,
            'real_data': True
        },
        'active_signals': len(current_signals),
        'last_update': last_update.isoformat() if last_update else None,
        'version': '4.1.0'
    })

@app.route('/api/stats')
def get_stats():
    total_signals = len(signal_history)
    successful = len([s for s in signal_history if s.get('result') == 'profit'])
    
    return jsonify({
        'performance': {
            'total_signals': total_signals,
            'successful_signals': successful,
            'success_rate': round((successful / total_signals * 100) if total_signals > 0 else 0, 1),
            'active_signals': len(current_signals)
        },
        'system': {
            'data_source': 'CoinGecko Real APIs',
            'update_frequency': '3 minutes',
            'signal_duration': '30 minutes',
            'min_confidence': 65
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/history')
def get_history():
    return jsonify({
        'history': signal_history[-30:],  # Últimos 30
        'total_count': len(signal_history),
        'data_source': 'real_analysis',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Iniciando Sistema de Sinais com Dados Reais v4.1 - Simplificado")
    print("📊 Fonte: CoinGecko API")
    print("🎯 Foco: Meme Coins + Principais")
    print("⚡ Atualização: A cada 3 minutos")
    print("🔧 Versão: Sem dependências pesadas")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

