import requests
import time

#curl -X POST http://localhost:8080/deploy \
#     -H "Content-Type: application/json" \
#     -d '{"namespace": "default", "image": "nginx"}
# curl -X GET http://localhost:8080/status/default/pod-nginx

BASE_URL = "http://localhost:8080"
NAMESPACE = "default"                          # namespace to deploy target application using deploymnt_service
IMAGE_NAME = "gcr.io/google-containers/pause"  # nginx
name = IMAGE_NAME.replace(":", "-").replace("/", "-")
POD_NAME = ("pod-" + name.lower()) if "-" not in name else name.lower()

def deploy():
    """ Deploys a pod to namspace """
    payload = {
        "namespace": NAMESPACE,
        "image": IMAGE_NAME
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(f"{BASE_URL}/deploy", json=payload, headers=headers)
    print("Deploy response:")
    print(response.status_code, response.text)

def check_status(timeout_seconds=180, interval_seconds=5):
    """ Check status of pod , polling for 3 mins (can be adjusted later) """
    max_attempts = timeout_seconds // interval_seconds
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/status/{NAMESPACE}/{POD_NAME}")
            print(f"Status response: {response.status_code}, {response.text}")
            if response.status_code == 200:
                data = response.json()
                print(f"Pod info : {data}")
                status = data.get("pod_status")
                if status and status.lower() == "running":
                    print("Congrts! pod is running! Exiting loop.")
                    return True
                else:
                    print(f"Pod status is : {status}")
            elif response.status_code == 404:
                print(f"Attempt {attempt+1}: Pod not found yet. Retrying...")
            else:
                print(f"Attempt {attempt+1}: Unexpected status code {response.status_code}")

        except requests.exceptions.RequestException as e:
            print("Error connecting to server:", e)
        print(f"Pod not running yet. Waiting {interval_seconds} seconds...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    deploy()
    time.sleep(3)
    check_status()
