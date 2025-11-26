
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import random
import time
import threading

app = Flask(__name__)

# Simulated apps
apps = {
    "WhatsApp": True,
    "Instagram": True,
    "Gmail": True
}

# Prometheus metrics para simulación
app_status_gauge = Gauge('app_status', 'Status of each app (1=active, 0=inactive)', ['app'])
app_error_gauge = Gauge('app_errors', 'Number of errors per app', ['app'])

# Error counters
error_counts = {
    "WhatsApp": 0,
    "Instagram": 0,
    "Gmail": 0
}

# Métricas para dashboard
REQUEST_COUNT = Counter('flask_http_request_total', 'Total HTTP requests', ['method', 'endpoint'])
ERROR_COUNT = Counter('flask_http_request_errors_total', 'Total HTTP errors', ['method', 'endpoint'])
LATENCY = Histogram('flask_request_latency_seconds', 'Request latency', ['endpoint'])

# Función para simular cambios de estado de apps
def simulate_app_status():
    while True:
        for app_name in apps:
            status = random.choice([True, True, True, False])  # Más probabilidad de estar activo
            apps[app_name] = status
            app_status_gauge.labels(app=app_name).set(1 if status else 0)
            if not status:
                error_counts[app_name] += 1
                app_error_gauge.labels(app=app_name).set(error_counts[app_name])
        time.sleep(5)

# Middleware para medir latencia y contar requests/errores
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    latency = time.time() - request.start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()
    LATENCY.labels(endpoint=request.path).observe(latency)
    if response.status_code >= 500:
        ERROR_COUNT.labels(method=request.method, endpoint=request.path).inc()
    return response

@app.route('/')
def home():
    return jsonify({"message": "My Cellphone App."})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    # Iniciar simulación en hilo
    threading.Thread(target=simulate_app_status, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
