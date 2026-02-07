# Kubernetes (Optional)

This folder contains Kubernetes manifests for deployment. It does **not** affect local Docker Compose.

## What’s included

- `namespace.yaml` – isolated namespace
- `configmap.yaml` – frontend origin placeholders
- `secret.yaml` – DB credentials and DATABASE_URL
- `postgres.yaml` – Postgres StatefulSet + Service
- `api.yaml` – API Deployment + Service
- `frontend.yaml` – Frontend Deployment + Service
- `ingress.yaml` – HTTPS + routing + rate limit annotations

## Before applying

1. Build and push images:
   - `your-registry/qube-quant-api:latest`
   - `your-registry/qube-quant-frontend:latest`

2. Update:
   - `your-domain.com` in `ingress.yaml`
   - `VITE_API_BASE` in `frontend.yaml`
   - `DATABASE_URL` in `secret.yaml`

3. Apply:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml
```

## Notes

- Consider using a managed Postgres instead of the included StatefulSet for production.
- Add cert-manager for automatic TLS provisioning.
- Add NetworkPolicies if your cluster supports them.
