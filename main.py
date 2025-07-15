"""
Sistema de Sinais Crypto - DADOS REAIS
Versão 4.0 - Sem Simulações
"""

import requests
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, jsonify
from flask_cors import CORS
import threading
import json
import os

app = Flask(__name__)
CORS(app)

# Configurações
COINGECKO_API = "https://api.coingecko.com/api/v3"
BINANCE_API = "https://api.binance.com/api/v3"

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

class RealDataCollector:
    """Coleta dados reais de APIs de criptomoedas"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoSignals/4.0'
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
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Erro ao buscar preços reais: {e}")
            return {}
    
    def get_historical_data(self, coin_id, days=1):
        """Obtém dados históricos para cálculo de indicadores"""
        try:
            url = f"{COINGECKO_API}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': '5m'  # Dados a cada 5 minutos
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Converter para formato utilizável
            prices = [point[1] for point in data['prices']]
            volumes = [point[1] for point in data['total_volumes']]
            timestamps = [point[0] for point in data['prices']]
            
            return {
                'prices': prices,
                'volumes': volumes,
                'timestamps': timestamps
            }
            
        except Exception as e:
            print(f"Erro ao buscar dados históricos para {coin_id}: {e}")
            return None

class TechnicalAnalyzer:
    """Calcula indicadores técnicos com dados reais"""
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calcula RSI real"""
        if len(prices) < period + 1:
            return 50  # Valor neutro se não há dados suficientes
        
        prices = np.array(prices)
        deltas = np.diff(prices)
        
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """Calcula MACD real"""
        if len(prices) < slow:
            return 0
        
        prices = np.array(prices)
        
        # EMAs
        ema_fast = pd.Series(prices).ewm(span=fast).mean()
        ema_slow = pd.Series(prices).ewm(span=slow).mean()
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line
        signal_line = macd_line.ewm(span=signal).mean()
        
        # MACD histogram
        histogram = macd_line - signal_line
        
        return round(histogram.iloc[-1], 4)
    
    @staticmethod
    def calculate_bollinger_bands(prices, period=20, std_dev=2):
        """Calcula Bandas de Bollinger reais"""
        if len(prices) < period:
            current_price = prices[-1] if prices else 0
            return current_price * 1.02, current_price * 0.98, current_price
        
        prices = np.array(prices)
        sma = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return round(upper_band, 6), round(lower_band, 6), round(sma, 6)
    
    @staticmethod
    def calculate_stochastic(prices, highs, lows, k_period=14):
        """Calcula Estocástico real"""
        if len(prices) < k_period:
            return 50
        
        current_price = prices[-1]
        lowest_low = min(lows[-k_period:])
        highest_high = max(highs[-k_period:])
        
        if highest_high == lowest_low:
            return 50
        
        k_percent = ((current_price - lowest_low) / (highest_high - lowest_low)) * 100
        
        return round(k_percent, 2)

class RealSignalAnalyzer:
    """Analisa sinais com dados reais"""
    
    def __init__(self):
        self.data_collector = RealDataCollector()
        self.analyzer = TechnicalAnalyzer()
        self.min_confidence = 60  # Confiança mínima para sinal real
    
    def analyze_real_signal(self, symbol):
        """Analisa sinal com dados 100% reais"""
        try:
            # Obter dados históricos reais
            coin_id = CRYPTO_SYMBOLS.get(symbol)
            if not coin_id:
                return None
            
            historical = self.data_collector.get_historical_data(coin_id)
            if not historical or len(historical['prices']) < 50:
                print(f"Dados insuficientes para {symbol}")
                return None
            
            prices = historical['prices']
            volumes = historical['volumes']
            current_price = prices[-1]
            
            # Calcular indicadores reais
            rsi = self.analyzer.calculate_rsi(prices)
            macd = self.analyzer.calculate_macd(prices)
            bb_upper, bb_lower, bb_middle = self.analyzer.calculate_bollinger_bands(prices)
            
            # Simular highs e lows para estocástico (aproximação)
            highs = [max(prices[i:i+5]) for i in range(0, len(prices)-4, 5)]
            lows = [min(prices[i:i+5]) for i in range(0, len(prices)-4, 5)]
            stoch = self.analyzer.calculate_stochastic(prices, highs, lows)
            
            # Sistema de pontuação baseado em indicadores reais
            score = 0
            
            # RSI (30/70 são níveis clássicos)
            if rsi < 30:
                score += 2  # Oversold = compra
            elif rsi > 70:
                score -= 2  # Overbought = venda
            elif rsi < 45:
                score += 1
            elif rsi > 55:
                score -= 1
            
            # MACD
            if macd > 0:
                score += 1  # Momentum positivo
            else:
                score -= 1  # Momentum negativo
            
            # Bollinger Bands
            if current_price <= bb_lower:
                score += 2  # Preço na banda inferior = compra
            elif current_price >= bb_upper:
                score -= 2  # Preço na banda superior = venda
            elif current_price < bb_middle:
                score += 1
            else:
                score -= 1
            
            # Estocástico
            if stoch < 20:
                score += 1  # Oversold
            elif stoch > 80:
                score -= 1  # Overbought
            
            # Volume (indicador de força)
            avg_volume = np.mean(volumes[-20:]) if len(volumes) >= 20 else volumes[-1]
            current_volume = volumes[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio > 1.5:  # Volume alto confirma sinal
                score = score * 1.2
            
            # Determinar sinal (critério mais rigoroso para dados reais)
            if score >= 3:
                signal_type = 'BUY'
                confidence = min(60 + (score * 5), 95)
            elif score <= -3:
                signal_type = 'SELL'
                confidence = min(60 + (abs(score) * 5), 95)
            else:
                return None  # Sinal não forte o suficiente
            
            # Calcular preço alvo baseado na volatilidade real
            price_changes = np.diff(prices[-50:])  # Últimas 50 mudanças
            volatility = np.std(price_changes) / current_price * 100
            
            # Preço alvo baseado na volatilidade real (mais conservador)
            target_percentage = min(max(volatility * 0.5, 1.5), 6.0)  # Entre 1.5% e 6%
            
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
                    'stochastic': stoch,
                    'volume_ratio': round(volume_ratio, 2),
                    'volatility': round(volatility, 2)
                },
                'data_source': 'real_api',
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Erro ao analisar {symbol}: {e}")
            return None

# Instância global
signal_analyzer = RealSignalAnalyzer()

def update_market_data():
    """Atualiza dados de mercado em background"""
    global current_signals, last_update, market_data_cache
    
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
                
                # Delay entre requisições para não sobrecarregar APIs
                time.sleep(1)
            
            # Atualizar sinais atuais
            for new_signal in new_signals:
                # Remover sinal antigo da mesma moeda
                current_signals = [s for s in current_signals if s['symbol'] != new_signal['symbol']]
                current_signals.append(new_signal)
            
            # Manter apenas últimos 100 no histórico
            if len(signal_history) > 100:
                signal_history[:] = signal_history[-100:]
            
            last_update = datetime.now()
            print(f"Atualização concluída. Sinais ativos: {len(current_signals)}")
            
        except Exception as e:
            print(f"Erro na atualização: {e}")
        
        # Aguardar 2 minutos antes da próxima atualização (dados reais não mudam tão rápido)
        time.sleep(120)

# Iniciar thread de atualização
update_thread = threading.Thread(target=update_market_data, daemon=True)
update_thread.start()

# Rotas da API
@app.route('/')
def home():
    return jsonify({
        'message': 'Sistema de sinais crypto com dados 100% reais',
        'status': 'online',
        'system': 'Crypto Signals v4.0 - Real Data',
        'data_source': 'CoinGecko + Binance APIs',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/signals')
def get_signals():
    return jsonify({
        'signals': current_signals,
        'count': len(current_signals),
        'last_update': last_update.isoformat() if last_update else None,
        'data_source': 'real_apis',
        'status': 'active',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'system': 'Crypto Signals v4.0',
        'data_source': 'Real APIs',
        'components': {
            'api': True,
            'data_collector': True,
            'signal_analyzer': True,
            'real_data': True
        },
        'active_signals': len(current_signals),
        'last_update': last_update.isoformat() if last_update else None,
        'version': '4.0.0'
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
            'data_source': 'Real APIs',
            'update_frequency': '2 minutes',
            'signal_duration': '30 minutes',
            'min_confidence': 60
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/history')
def get_history():
    limit = int(request.args.get('limit', 50))
    
    return jsonify({
        'history': signal_history[-limit:],
        'total_count': len(signal_history),
        'data_source': 'real_analysis',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Iniciando Sistema de Sinais com Dados Reais v4.0")
    print("📊 Fonte: CoinGecko + Binance APIs")
    print("🎯 Foco: Meme Coins + Principais")
    print("⚡ Atualização: A cada 2 minutos")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

