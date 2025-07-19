from flask import Flask, jsonify
from datetime import datetime
import time
from .signals import generate_signal  # Importa a lógica de sinais
from ..config import CRYPTOS, MIN_CONFIDENCE  # Importa configurações

app = Flask(__name__)

# Dados mock (substitua por um DB real depois)
SIGNALS_HISTORY = []
SYSTEM_STATS = {
    "uptime": "99.9%",
    "success_rate": "82%",
    "last_update": datetime.now().isoformat()
}

# --- Endpoints ---
@app.route("/")
def status():
    return jsonify({
        "system": "Crypto Signals v3.0",
        "status": "online",
        "cryptos": CRYPTOS,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "uptime": SYSTEM_STATS["uptime"],
        "latency": "<100ms"
    })

@app.route("/api/signals")
def signals():
    signal = generate_signal()
    if not signal:
        return jsonify({"error": "Cooldown ativo. Tente novamente em 5 minutos."}), 429
    
    SIGNALS_HISTORY.append(signal)  # Registra no histórico
    return jsonify(signal)

@app.route("/api/stats")
def stats():
    return jsonify(SYSTEM_STATS)

@app.route("/api/history")
def history():
    return jsonify({
        "count": len(SIGNALS_HISTORY),
        "signals": SIGNALS_HISTORY[-10:]  # Últimos 10 sinais
    })

# --- Filtros do Sistema (Exemplo) ---
@app.route("/api/coins/<symbol>")
def coin_data(symbol):
    if symbol.upper() not in CRYPTOS:
        return jsonify({"error": "Moeda não suportada"}), 404
    
    return jsonify({
        "symbol": symbol.upper(),
        "signal": "NEUTRAL",
        "confidence": "65%"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
