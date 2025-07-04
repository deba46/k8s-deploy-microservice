
## Project Overview
A minimal Python-based microservice that automates the deployment of a public Docker image to a Kubernetes (k8s) cluster and provides real-time status updates of the deployed pods. Please note that this is only deploying as a "Pod" and not a deployment yet.
Tech Stack :
kubernetes client lib,
minikube,
fastApi


```bash
# Clone the repository
git clone https://github.com/deba46/k8s-deploy-microservice.git
cd k8s-deploy-microservice

python3 -m venv venv
source venv/bin/activate

# Create venv with python >= 3.11 & Install dependencies
pip install -r requirements.txt
# Set minikube docker env
eval $(minikube docker-env)
# Build the image 
docker build -t k8s-deployment-service:v001 .
# Deploy service using kubectl
kubectl apply -f deployment.yaml
kubectl apply -f deployer-rbac,yaml
# Run make , covers functional e2e tests
# Update clinet apps to change namespace name, images etc.
#
make
# To run unit tests
PYTHONPATH=. pytest tests/
```
# Open questions
### 1. Security

### 2. Scalability

### 3. Monitoring

## TODO:
- Add code for "deployment" 
- Integrate helm charts and k8s manfiest via client lib 
- Explore kubernetes_asyncio.test package possibly for async tests
- Explore kubernetes_asyncio.watch package for real time status/monitoring
- load testing using tools like locust

## Screenshots
Api Docs:
![alt text](images/image.png)
To open docs : minikube service deployment-service -n deployment-service

K8s Apps:
![alt text](images/image-1.png)

Run result:
![alt text](images/image-2.png)

Trying to deploy an invalid Image :
![alt text](images/image-3.png)
