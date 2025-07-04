
PYTHON_SCRIPT = "microservice_client.py"


all: port-forward run-script

port-forward:
	@echo "Starting port forwarding..."
	kubectl port-forward svc/deployment-service 8080:80 -n deployment-service > /dev/null 2>&1 & echo $! > port-forward.pid
	sleep 2

run-script:
	@echo "Running client script..."
	python3 $(PYTHON_SCRIPT)


stop:
	@echo "Killing port-forward processes..."
	-pkill -f "kubectl port-forward"
clean: stop
	@echo "Cleaned up background processes.."
