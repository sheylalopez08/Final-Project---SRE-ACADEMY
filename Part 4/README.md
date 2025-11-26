# Guía Completa: Prometheus + OpenTelemetry Collector en Minikube

## 📌 Introducción
Este documento describe:
- Cómo desplegar Prometheus en Minikube.
- Cómo resolver errores de scraping relacionados con OpenTelemetry Collector.
- Cómo automatizar el despliegue con Ansible.
- Comandos de verificación y manifiestos completos.

---

## ✅ Despliegue de Prometheus
1. Aplicar el manifiesto:
```bash
kubectl apply -f prometheus.yaml
```

2. Verificar pods:
```bash
kubectl get pods -n monitoring
```

3. Acceder a la UI de Prometheus:
```bash
minikube service prometheus-service -n monitoring
```

---

## ⚠️ Problema Encontrado
Error en el dashboard:
```
Error scraping target: Get "http://otel-collector.opentelemetry.svc.cluster.local:9464/metrics": dial tcp: lookup otel-collector.opentelemetry.svc.cluster.local on 10.96.0.10:53: no such host
```

### Causa
El namespace `opentelemetry` y el Service `otel-collector` no existían.

---

## 🔍 Solución
1. Crear namespace:
```bash
kubectl create namespace opentelemetry
```

2. Aplicar manifiesto del Collector:
```bash
kubectl apply -f otel-collector.yaml
```

3. Cambiar imagen a `contrib` para soportar `resourcedetection`:
```bash
kubectl -n opentelemetry set image deployment/otel-collector   otel-collector=otel/opentelemetry-collector-contrib:0.102.0
```

4. Verificar pods y servicios:
```bash
kubectl get pods -n opentelemetry
kubectl get svc -n opentelemetry
```

---

## 📄 Manifiesto completo `otel-collector.yaml`
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: opentelemetry
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
  namespace: opentelemetry
data:
  otel-collector-config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
    processors:
      batch:
        timeout: 5s
        send_batch_size: 8192
      memory_limiter:
        check_interval: 5s
        limit_percentage: 80
        spike_limit_percentage: 25
      resourcedetection:
        detectors: [env, system]
        timeout: 2s
    exporters:
      prometheus:
        endpoint: 0.0.0.0:9464
        namespace: otel
        const_labels:
          service: otel-collector
    extensions:
      health_check:
        endpoint: 0.0.0.0:13133
    service:
      telemetry:
        logs:
          level: info
      extensions: [health_check]
      pipelines:
        metrics:
          receivers: [otlp]
          processors: [memory_limiter, batch, resourcedetection]
          exporters: [prometheus]
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otel-collector
  namespace: opentelemetry
spec:
  replicas: 1
  selector:
    matchLabels:
      app: otel-collector
  template:
    metadata:
      labels:
        app: otel-collector
    spec:
      containers:
        - name: otel-collector
          image: otel/opentelemetry-collector-contrib:latest
          args:
            - "--config=/etc/otelcol/otel-collector-config.yaml"
          ports:
            - containerPort: 4317
            - containerPort: 4318
            - containerPort: 9464
            - containerPort: 13133
          volumeMounts:
            - name: otel-config
              mountPath: /etc/otelcol
      volumes:
        - name: otel-config
          configMap:
            name: otel-collector-config
            items:
              - key: otel-collector-config.yaml
                path: otel-collector-config.yaml
---
apiVersion: v1
kind: Service
metadata:
  name: otel-collector
  namespace: opentelemetry
spec:
  selector:
    app: otel-collector
  ports:
    - name: prometheus
      port: 9464
      targetPort: 9464
    - name: otlp-grpc
      port: 4317
      targetPort: 4317
    - name: otlp-http
      port: 4318
      targetPort: 4318
```

---

## 🤖 Automatización con Ansible
### Playbook minimalista (`infra.yaml`)
```yaml
---
- name: Apply Prometheus and OpenTelemetry Collector configuration in Minikube
  hosts: local
  gather_facts: false

  tasks:
    - name: Apply Prometheus configuration
      command: kubectl apply -f prometheus.yaml
      args:
        chdir: "/Users/sheyla.lopez/Documents/FINAL PROJECT - SRE ACADEMY/Final Project /My Cellphone App/Part 4"

    - name: Apply OpenTelemetry Collector configuration
      command: kubectl apply -f otel-collector.yaml
      args:
        chdir: "/Users/sheyla.lopez/Documents/FINAL PROJECT - SRE ACADEMY/Final Project /My Cellphone App/Part 4"

    - name: Reminder to access Prometheus UI
      debug:
        msg: "Ejecuta: minikube service prometheus-service -n monitoring"
```

### Ejecución
```bash
ansible-playbook -i "Part 3.1/Ansible/inventory.ini" "/Users/sheyla.lopez/Documents/FINAL PROJECT - SRE ACADEMY/Final Project /My Cellphone App/Part 4/infra.yaml"
```

---

## ✅ Resultado del Playbook y Verificación
### Salida exitosa
```
PLAY [Apply Prometheus and OpenTelemetry Collector configuration in Minikube] *************************************************
TASK [Apply Prometheus configuration] *****************************************************************************************
changed: [localhost]
TASK [Apply OpenTelemetry Collector configuration] ****************************************************************************
changed: [localhost]
TASK [Reminder to access Prometheus UI] ***************************************************************************************
ok: [localhost] => {
    "msg": "Ejecuta: minikube service prometheus-service -n monitoring"
}
PLAY RECAP ********************************************************************************************************************
localhost                  : ok=3    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

### Comandos de verificación rápida
```bash
kubectl get pods -n monitoring
kubectl get pods -n opentelemetry
kubectl get svc -n opentelemetry
kubectl get endpoints otel-collector -n opentelemetry
minikube service prometheus-service -n monitoring
kubectl -n monitoring exec -it <POD_PROMETHEUS> -- sh -c 'wget -qO- http://otel-collector.opentelemetry.svc.cluster.local:9464/metrics | head'
```

---
