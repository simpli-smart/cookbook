import os
from time import sleep

from dotenv import load_dotenv
from simplismart import (
    Simplismart,
    ModelRepoCompileAvatar,
    ModelRepoCompileCreate,
    ModelRepoListParams,
    DeploymentCreate,
)

load_dotenv()

client = Simplismart(pg_token=os.getenv("SIMPLISMART_PG_TOKEN"))
org_id = os.getenv("ORG_ID")

MODEL_NAME = "gemma-4-12B-it"
# repo = {}
# repo["uuid"] = "11fd6357-8d08-4013-ab07-937a30c939a3"
# deployment = {}
# deployment["deployment_id"] = "3fe821d9-9992-44fa-be56-b7e19b1ba80a"

# 1. Compile Gemma 4 12B from Hugging Face, optimised for H100
client.create_model_repo_private_compile(
    ModelRepoCompileCreate(
        name=MODEL_NAME,
        avatar=ModelRepoCompileAvatar(
            image_url=f"https://ui-avatars.com/api/?background=f3f3f3&color=000000&name={MODEL_NAME}"
        ),
        source_type="huggingface",
        source_url="google/gemma-4-12B-it",
        model_class="Gemma4UnifiedForConditionalGeneration",
        accelerator_type="nvidia-h100",
        use_simplismart_infrastructure=True,
    )
)

# 2. Wait until compilation finishes
while True:
    repo = client.list_model_repos(
        ModelRepoListParams(org_id=org_id, name=MODEL_NAME, count=1)
    )["results"][0]
    print("Compilation status:", repo["status"])
    if repo["status"] == "SUCCESS":
        break
    sleep(30)

# 3. Deploy the compiled model on an H100 (autoscale 1–2 replicas on GPU usage)
deployment = client.create_deployment(
    DeploymentCreate(
        org=org_id,
        model_repo=repo["uuid"],
        gpu_id="nvidia-h100",
        name=MODEL_NAME,
        min_pod_replicas=1,
        max_pod_replicas=2,
        autoscale_config={"targets": [{"metric": "gpu", "target": 80}]},
    )
)
print("Endpoint:", f"https://{deployment.get('model_endpoint', '')}")

# 4. Poll health until the deployment is ready
while True:
    health = client.fetch_deployment_health(deployment_id=deployment["deployment_id"])
    status = health.get("data", "unknown")
    print("Health:", status)
    if status == "Healthy":
        print("Deployment is ready.")
        break
    sleep(30)
