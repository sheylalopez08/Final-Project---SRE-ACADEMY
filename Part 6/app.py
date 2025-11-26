import os
from flask import Flask, request, jsonify
# Try to import prometheus_client; provide no-op fallbacks if it's not installed so the app can run.
try:
    import importlib
    _prom = importlib.import_module('prometheus_client')
    Counter = getattr(_prom, 'Counter')
    Histogram = getattr(_prom, 'Histogram')
    Gauge = getattr(_prom, 'Gauge')
    generate_latest = getattr(_prom, 'generate_latest')
    CONTENT_TYPE_LATEST = getattr(_prom, 'CONTENT_TYPE_LATEST')
except Exception:
    class _NoopMetric:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def inc(self, *args, **kwargs):
            return None
        def set(self, *args, **kwargs):
            return None
        def observe(self, *args, **kwargs):
            return None

    def generate_latest():
        return b''

    CONTENT_TYPE_LATEST = 'text/plain; version=0.0.4; charset=utf-8'
    Counter = _NoopMetric
    Histogram = _NoopMetric
    Gauge = _NoopMetric

import random
import time
import threading

# OpenTelemetry imports (optional; provide no-op fallbacks if not installed)
try:
    import importlib
    _otel = importlib.import_module('opentelemetry')
    trace = getattr(_otel, 'trace')
    _instr = importlib.import_module('opentelemetry.instrumentation.flask')
    FlaskInstrumentor = getattr(_instr, 'FlaskInstrumentor')
    _res = importlib.import_module('opentelemetry.sdk.resources')
    Resource = getattr(_res, 'Resource')
    _trace_sdk = importlib.import_module('opentelemetry.sdk.trace')
    TracerProvider = getattr(_trace_sdk, 'TracerProvider')
    _export_mod = importlib.import_module('opentelemetry.sdk.trace.export')
    BatchSpanProcessor = getattr(_export_mod, 'BatchSpanProcessor')
    _otlp_mod = importlib.import_module('opentelemetry.exporter.otlp.proto.grpc.trace_exporter')
    OTLPSpanExporter = getattr(_otlp_mod, 'OTLPSpanExporter')
    telemetry_available = True
except Exception:
    # Minimal no-op shims so the app can run without opentelemetry installed
    import contextlib

    telemetry_available = False

    class DummyTracer:
        @contextlib.contextmanager
        def start_as_current_span(self, name):
            yield

    class TraceShim:
        def __init__(self):
            self._tracer = DummyTracer()

        def get_tracer(self, name):
            return self._tracer

        def set_tracer_provider(self, provider):
            pass

        def get_tracer_provider(self):
            class Provider:
                def add_span_processor(self, processor):
                    pass
            return Provider()

    trace = TraceShim()

    class FlaskInstrumentor:
        @staticmethod
        def instrument_app(app):
            return None

    class Resource:
        @staticmethod
        def create(attrs):
            return attrs

    class TracerProvider:
        def __init__(self, *args, **kwargs):
            pass

    class BatchSpanProcessor:
        def __init__(self, exporter):
            pass

    class OTLPSpanExporter:
        def __init__(self, *args, **kwargs):
            pass

# Configure OpenTelemetry using environment variables
service_name = os.getenv("OTEL_SERVICE_NAME", "my-cellphone-app")
endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")

# Set up tracer provider and exporter only if telemetry is available
if telemetry_available:
    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({"service.name": service_name}))
    )
    otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# ✅ Define tracer AFTER provider is set
tracer = trace.get_tracer(__name__)

# Flask app setup
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

# Simulated apps
apps = {
    "WhatsApp": True,
    "Instagram": True,
    "Gmail": True
}

# Prometheus metrics for simulation
app_status_gauge = Gauge('app_status', 'Status of each app (1=active, 0=inactive)', ['app'])
app_error_gauge = Gauge('app_errors', 'Number of errors per app', ['app'])

# Error counters
error_counts = {
    "WhatsApp": 0,
    "Instagram": 0,
    "Gmail": 0
}

# Metrics for dashboard
REQUEST_COUNT = Counter('flask_http_request_total', 'Total HTTP requests', ['method', 'endpoint'])
ERROR_COUNT = Counter('flask_http_request_errors_total', 'Total HTTP errors', ['method', 'endpoint'])
LATENCY = Histogram('flask_request_latency_seconds', 'Request latency', ['endpoint'])

def simulate_app_status():
    while True:
        for app_name in apps:
            status = random.choice([True, True, True, False])  # Higher chance of being active
            apps[app_name] = status
            app_status_gauge.labels(app=app_name).set(1 if status else 0)
            if not status:
                error_counts[app_name] += 1
                app_error_gauge.labels(app=app_name).set(error_counts[app_name])
        time.sleep(5)

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
    with tracer.start_as_current_span('home-endpoint'):
        return jsonify({"message": "My Cellphone App."})

@app.route('/metrics')
def metrics():
    try:
        tracer = trace.get_tracer(__name__)  # Asegura que tracer esté definido
        with tracer.start_as_current_span('metrics-endpoint'):
            return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    except Exception as e:
        app.logger.error(f'Metrics endpoint error: {e}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    threading.Thread(target=simulate_app_status, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)