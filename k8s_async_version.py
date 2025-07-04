import logging
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from kubernetes_asyncio import client, config
from kubernetes_asyncio.client.rest import ApiException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global core_v1_api
    try:
        config.load_incluster_config()
        logger.info("Loaded in-cluster Kubernetes config..")
    except config.ConfigException:
        config.load_kube_config()
        logger.info("Loaded local kubeconfig..")
    core_v1_api = client.CoreV1Api()
    logger.info("Kubernetes CoreV1Api client initialized.")
    yield  

app = FastAPI(lifespan=lifespan)

class DeployRequest(BaseModel):
    image: str
    namespace: str  

@app.post("/deploy")
async def deploy_pod(req: DeployRequest):
    """ Deploys a pod to k8s namespace """
    name = req.image.replace(":", "-").replace("/", "-")
    pod_name = ("pod-" + name.lower()) if "-" not in name else name.lower()

    if core_v1_api is None:
        logger.error("Kubernetes client not initialized!!")
        raise RuntimeError("Kubernetes client not initialized..")
    
    logger.info(f"Received request to deploy pod-> image={req.image}, namespace={req.namespace}")
    
    try:
        await core_v1_api.read_namespace(req.namespace)
        logger.info(f"Namespace '{req.namespace}' exists..")
    except ApiException as e:
        if e.status == 404:
            logger.warning(f"Namespace '{req.namespace}' not found!")
            raise HTTPException(status_code=400, detail=f"Namespace '{req.namespace}' does not exist.")
        else:
            logger.error("Error while checking namespace existence.!")
            raise HTTPException(status_code=500, detail=f"Namespace check failed: {e}")
    # TODO  - further enhancement
    # add more params (vol mounts, env variables , security context etc.)to manifest, dynamic set by user
    pod_manifest = client.V1Pod(
        metadata=client.V1ObjectMeta(name=pod_name, labels={"app": "deployment-service"}),
        spec=client.V1PodSpec(
            containers=[client.V1Container(
                name="app-container",
                image=req.image,
                ports=[client.V1ContainerPort(container_port=80)]
            )],
            restart_policy="Always"
        )
    )
    #TODO - further enhancement
    # add code to create Deployment -V1Deployment
    try:
        await core_v1_api.create_namespaced_pod(namespace=req.namespace, body=pod_manifest)
        logger.info(f"Pod '{pod_name}' created successfully in namespace '{req.namespace}'..")
    except ApiException as e:
        if e.status == 409:
            raise HTTPException(status_code=409, detail=f"Pod '{pod_name}' already exists in namespace '{req.namespace}'.")
        else:
            logger.exception("Failed to create pod!!")
            raise HTTPException(status_code=500, detail=f"Failed to create pod: {e}")

    return {"message": "Pod deployment initiated", "pod_name": pod_name, "namespace": req.namespace}

@app.get("/status/{namespace}/{pod_name}")
async def pod_status(namespace: str, pod_name: str):
    """ 
     Check status of pod in a namespace 
     #TODO - enhancement : replace by kubernetes_asyncio.watch api 
    """
    logger.info(f"Fetching status for pod '{pod_name}' in namespace '{namespace}'.")
    try:
        pod = await core_v1_api.read_namespaced_pod(name=pod_name, namespace=namespace)
    except ApiException as e:
        if e.status == 404:
            logger.warning(f"Pod '{pod_name}' not found in namespace '{namespace}'.")
            raise HTTPException(status_code=404, detail="Pod not found")
        else:
            logger.exception("Error fetching pod status.")
            raise HTTPException(status_code=500, detail=f"Error fetching pod status: {e}")

    status = pod.status.phase
    #pod_ip = pod.status.pod_ip
    start_time = pod.status.start_time
    # TODO - further enhancement
    # Check for more erros/msgs , handle multiple containers 
    container_statuses = pod.status.container_statuses or []
    container_state = "Unknown"
    if container_statuses:
        state = container_statuses[0].state
        if state.waiting:
            container_state = f"Waiting: {state.waiting.reason}"
        elif state.running:
            container_state = "Running"
        elif state.terminated:
            container_state = f"Terminated: {state.terminated.reason}"
    
    logger.info(f"Pod '{pod_name}' status: {status}, container state: {container_state}")
    return {
        "pod_name": pod.metadata.name,
        "namespace": namespace,
        "pod_status": status,
        "container_state": container_state,
        "start_time": start_time,
        "Owners": pod.metadata.owner_references
    }

    ## Pod metadata from api
    #name: pod name (str)
    #namespace: namespace name (str)
    #labels: dict of labels (Dict[str, str])
    #annotations: dict of annotations (Dict[str, str])
    #uid: unique ID (str)
    #resource_version: resource version (str)
    #generation: generation number (int)
    #creation_timestamp: datetime when created (datetime.datetime)
    #deletion_timestamp: datetime when deletion was requested (datetime.datetime or None)
    #owner_references: list of owners (List[V1OwnerReference])
    #finalizers: list of finalizers (List[str])
    #cluster_name: cluster name (str)
    #managed_fields: list of managed fields (List[V1ManagedFieldsEntry])
