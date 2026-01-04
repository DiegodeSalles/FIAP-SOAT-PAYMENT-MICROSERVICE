kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f mongo-deployment.yaml
kubectl apply -f mongo-pvc.yaml
kubectl apply -f mongo-service.yaml
kubectl apply -f payment-deployment.yaml
kubectl apply -f payment-service.yaml