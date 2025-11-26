
# Part 3 – Kubernetes Deployment with Minikube

This section describes how to deploy the Flask-based mobile app simulation using Kubernetes and Minikube.

## 📦 Project Overview

- **App Name:** `my-cellphone-app`
- **Deployment Type:** Kubernetes
- **Environment:** Local using Minikube
- **Image Source:** Docker Hub (`sheylalopez08/my-cellphone-app:latest`)

## 🚀 Steps to Deploy

### 1. Start Minikube
```bash
minikube start
```

### 2. Apply Deployment
```bash
kubectl apply -f deployment.yaml
```

### 3. Apply Service
```bash
kubectl apply -f service.yaml
```

### 5. Access the App
```bash
minikube service my-cellphone-app-service
```

## 🔍 Troubleshooting

- **ErrImagePull:** Ensure the image name is correct and accessible from Docker Hub.
- **Only one pod running:** Check replica count in `deployment.yaml` and reapply.
- **Service not reachable:** Confirm service type is `NodePort` and use `minikube service` to access.


