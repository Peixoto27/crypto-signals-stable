import ccxt
import talib
import numpy as np
from datetime import datetime
from typing import Optional, Dict

class SignalGenerator:
    def __init__(self, api_key: str, api_secret: str):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True
        })

    def analyze(self, symbol: str, timeframe: str = '1h') -> Optional[Dict]:
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=100)
            closes = np.array([x[4] for x in ohlcv], dtype=float)
            
            # Indicadores reais
            rsi = talib.RSI(closes, timeperiod=14)[-1]
            macd, _, _ = talib.MACD(closes)
            last_macd = macd[-1]

            signal = {
                "symbol": symbol,
                "timestamp": datetime.utcnow().isoformat(),
                "indicators": {
                    "rsi": round(rsi, 2),
                    "macd": round(last_macd, 4)
                }
            }

            if rsi < 30 and last_macd > 0:
                signal["action"] = "STRONG_BUY"
            elif rsi > 70 and last_macd < 0:
                signal["action"] = "STRONG_SELL"
            else:
                signal["action"] = "HOLD"

            return signal

        except Exception as e:
            print(f"Error analyzing {symbol}: {str(e)}")
            return None
