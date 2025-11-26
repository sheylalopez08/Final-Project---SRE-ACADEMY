# My Cellphone App – Kubernetes Observability Project

## 📖 Project Overview
This project demonstrates how to deploy a Python Flask application exposing Prometheus metrics, integrate it with Prometheus, Grafana, and Alertmanager in a Kubernetes cluster, and visualize observability data.

### ✅ Project Stages
1. **Application with Metrics**
   - Simple API exposing metrics at `/metrics` using `prometheus_client`.
2. **Deployment in Kubernetes**
   - Deployment and Service YAML files.
3. **Prometheus Setup**
   - Scraping configuration for the application.
4. **Grafana Setup**
   - Dashboards connected to Prometheus.
5. **Alertmanager Setup**
   - Real alert destination (Slack, Email, Teams).
6. **Documentation on GitHub**
   - README, LICENSE, CONTRIBUTING, screenshots.

---

## 📸 Screenshots Gallery

### Part 1: Application with Metrics
*(Add screenshots here)*

### Part 2: Docker & App Running
![Docker Hub Repositories](docs/screenshots/part2/docker-hub.png)
*Docker Hub showing published images for the application.*

![Flask App Running](docs/screenshots/part2/flask-app.png)
*My Cellphone App running locally on port 5000.*

### Part 3: Kubernetes Deployment
![Kubernetes Deployment](docs/screenshots/part3/kubernetes-deployment.png)
*Application deployed in Kubernetes using Minikube.*

### Part 4: Prometheus Setup
*(Add screenshots here)*

### Part 5: Grafana Dashboards
![Grafana Dashboard](docs/screenshots/part5/grafana-dashboard2.png)
*Dashboard showing RPS, latency, and availability metrics.*

![Grafana Panel Editor](docs/screenshots/part5/grafana-1.png)
*Panel editor in Grafana with Prometheus query for CPU usage.*

![Grafana Resource Usage](docs/screenshots/part5/grafana-2.png)
*Dashboard showing CPU, memory, and filesystem usage per pod.*

### Part 6: Alertmanager Setup
*(Add screenshots here)*

---

## 📂 Folder Structure
```
project_docs/
├── README.md
└── docs/
    └── screenshots/
        ├── part1/
        ├── part2/
        ├── part3/
        ├── part4/
        ├── part5/
        └── part6/
```

## ✅ How to Use
- Place your screenshots in the corresponding `docs/screenshots/partX/` folder.
- Update the README.md with correct image names if needed.
