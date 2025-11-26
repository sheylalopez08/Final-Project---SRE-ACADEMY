#!/bin/bash

# Namespaces
APP_NAMESPACE="my-cellphone"
OTEL_NAMESPACE="opentelemetry"

# Base directory (project root)
BASE_DIR=$(pwd)

# File paths
DEPLOYMENT="$BASE_DIR/Part 6/deployment.yaml"
SERVICE="$BASE_DIR/Part 6/service.yaml"
JAEGER="$BASE_DIR/Part 6/jaeger.yaml"
COLLECTOR="$BASE_DIR/Part 6/otel-collector.yaml"
PROMETHEUS="$BASE_DIR/Part 4/prometheus.yaml"
GRAFANA="$BASE_DIR/Part 5/grafana.yaml"

# Function to check if file exists
check_file() {
  if [ ! -f "$1" ]; then
    echo "ERROR: File $1 not found. Please verify the path."
    exit 1
  fi
}

# Check all files exist
check_file "$DEPLOYMENT"
check_file "$SERVICE"
check_file "$JAEGER"
check_file "$COLLECTOR"
check_file "$PROMETHEUS"
check_file "$GRAFANA"

# Create namespaces if not exist
echo "Creating namespaces if they don't exist..."
kubectl get namespace $APP_NAMESPACE >/dev/null 2>&1 || kubectl create namespace $APP_NAMESPACE
kubectl get namespace $OTEL_NAMESPACE >/dev/null 2>&1 || kubectl create namespace $OTEL_NAMESPACE

# 1. Deploy Flask app in my-cellphone namespace
echo "Deploying Flask app in namespace $APP_NAMESPACE..."
kubectl apply -n $APP_NAMESPACE -f "$DEPLOYMENT"
kubectl apply -n $APP_NAMESPACE -f "$SERVICE"

# Wait for Flask app pod to be ready
echo "Waiting for Flask app to be ready..."
kubectl wait --for=condition=Ready pod -l app=my-cellphone-app -n $APP_NAMESPACE --timeout=180s

# 2. Deploy Jaeger in opentelemetry namespace
echo "Deploying Jaeger..."
kubectl apply -n $OTEL_NAMESPACE -f "$JAEGER"

# Wait for Jaeger pod to be ready
echo "Waiting for Jaeger to be ready..."
kubectl wait --for=condition=Ready pod -l app=jaeger -n $OTEL_NAMESPACE --timeout=180s

# 3. Deploy OpenTelemetry Collector
echo "Applying OpenTelemetry Collector configuration..."
kubectl apply -n $OTEL_NAMESPACE -f "$COLLECTOR"

# Wait for Collector pod to be ready
echo "Waiting for OpenTelemetry Collector to be ready..."
kubectl wait --for=condition=Ready pod -l app=otel-collector -n $OTEL_NAMESPACE --timeout=180s

# 4. Deploy Prometheus and Grafana
echo "Deploying Prometheus and Grafana..."
kubectl apply -n $APP_NAMESPACE -f "$PROMETHEUS"
kubectl apply -n $APP_NAMESPACE -f "$GRAFANA"

# Wait for Prometheus and Grafana pods to be ready
echo "Waiting for Prometheus and Grafana to be ready..."
kubectl wait --for=condition=Ready pod -l app=prometheus -n $APP_NAMESPACE --timeout=180s
kubectl wait --for=condition=Ready pod -l app=grafana -n $APP_NAMESPACE --timeout=180s


# Aplicar Prometheus actualizado y Alertmanager
kubectl apply -n $APP_NAMESPACE -f "$PROMETHEUS"
kubectl apply -n $APP_NAMESPACE -f "$BASE_DIR/Part 6/alertmanager.yaml"

# Esperar que Alertmanager esté listo
kubectl wait --for=condition=Ready pod -l app=alertmanager -n $APP_NAMESPACE --timeout=180s

# Port-forward para Alertmanager
echo "Starting port-forward for Alertmanager on port 9093..."
kubectl port-forward svc/alertmanager -n $APP_NAMESPACE 9093:9093 &
ALERTMANAGER_PID=$!
echo "Alertmanager is accessible at: http://localhost:9093"

# Port-forward services
echo "Starting port-forward for Grafana on port 3000..."
kubectl port-forward svc/grafana -n $APP_NAMESPACE 3000:3000 &
GRAFANA_PID=$!
echo "Grafana is accessible at: http://localhost:3000"

echo "Starting port-forward for Prometheus on port 9090..."
kubectl port-forward svc/prometheus-service -n $APP_NAMESPACE 9090:9090 &
PROMETHEUS_PID=$!
echo "Prometheus is accessible at: http://localhost:9090"

echo "Starting port-forward for Jaeger on port 16686..."
kubectl port-forward svc/jaeger -n $OTEL_NAMESPACE 16686:16686 &
JAEGER_PID=$!
echo "Jaeger UI is accessible at: http://localhost:16686"

echo "Starting port-forward for OpenTelemetry Collector metrics on port 9464..."
kubectl port-forward svc/otel-collector -n $OTEL_NAMESPACE 9464:9464 &
COLLECTOR_PID=$!
echo "Collector metrics are accessible at: http://localhost:9464/metrics"

# Trap to kill background processes on exit
trap "kill $GRAFANA_PID $PROMETHEUS_PID $JAEGER_PID $COLLECTOR_PID $ALERTMANAGER_PID" EXIT

# Keep script running to maintain port-forwarding
echo "Port-forwarding active. Press Ctrl+C to stop."
wait
