kubectl delete -f payment-service.yaml
kubectl delete -f payment-deployment.yaml
kubectl delete -f mongo-service.yaml
kubectl delete -f mongo-deployment.yaml
kubectl delete -f mongo-pvc.yaml
kubectl delete -f secret.yaml
kubectl delete -f configmap.yaml
