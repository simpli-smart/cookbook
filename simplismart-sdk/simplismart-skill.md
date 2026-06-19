# Simplismart Skill

You are a Simplismart couple with Claude Code. When this skill is invoked, help the user deploy, manage, and scale AI models on Simplismart using the Simplismart CLI (`simplismart-sdk` installs both the Python SDK and the CLI).

Execute CLI commands directly via bash — no Python scripts needed.

---

## What This Skill Does

Detect user intent and execute one of these workflows:

| Intent | Workflow |
|---|---|
| Deploy a new model | Import → Compile → Poll status → Deploy → Health check |
| Check deployment status | List deployments / fetch health |
| Scale a deployment | Update autoscaling (min/max replicas) |
| Manage secrets | Create Docker Hub / Depot / NVIDIA NIM / HuggingFace credentials |
| Stop or delete a deployment | Stop / delete with confirmation |

---

## Step 0 — Environment Check

Before any workflow, verify the CLI is installed and credentials are set. If env vars are missing, auto-source a `.env` file from the working directory before prompting the user:

```bash
simplismart --help > /dev/null && echo "CLI OK"
echo "PG_TOKEN set: ${SIMPLISMART_PG_TOKEN:+yes}"
echo "ORG_ID: $ORG_ID"
```

If `SIMPLISMART_PG_TOKEN` or `ORG_ID` are not set, look for a `.env` file in the working directory and source it:

```bash
set -a && source .env && set +a
echo "PG_TOKEN set: ${SIMPLISMART_PG_TOKEN:+yes}"
echo "ORG_ID: $ORG_ID"
```

Use `set -a` so all variables exported from `.env` are available to subsequent commands in the same bash invocation. Prefix every CLI command with `set -a && source .env && set +a &&` to ensure creds are always in scope.

If no `.env` file exists and credentials are still missing, prompt the user:

> "Set these environment variables first:
> ```bash
> export SIMPLISMART_PG_TOKEN="your_pg_token_here"
> export ORG_ID="your_org_uuid"
> ```
> Or add them to a `.env` file in your working directory. Get your token from https://app.simplismart.ai/settings?tab=2"

If the CLI is not installed:

```bash
pip install simplismart-sdk
```

Note: the CLI does not support `--version`. Use `--help` to verify the install.

---

## Workflow 1 — Deploy a New Model from HuggingFace

**Trigger:** User says "deploy [model name]", "import from HuggingFace", or "run [HF model ID]"

Before starting, ask:
1. HuggingFace model ID (e.g. `meta-llama/Llama-3.2-1B-Instruct`)
2. Model class (e.g. `LlamaForCausalLM`) — if unsure, check the model's `config.json` on HuggingFace
3. Is the model gated? (Llama, Gemma, Mistral-Instruct variants require a HuggingFace token to download)
4. Deployment name (suggest a slug, e.g. `llama-3-2-1b`)
5. Min/max replicas (default: 1 / 4)
6. GPU utilization autoscale target (default: 80%)

### Step 1a (gated models only): Pre-flight checks and store HuggingFace token

Before storing the token, confirm:
> "Have you accepted the model license on HuggingFace? For example, visit huggingface.co/meta-llama/Llama-3.2-1B-Instruct and click 'Agree and access repository'. Compilation will fail with FAILED_OPTIMISING if this step is skipped."

Only proceed once the user confirms. Then store the token:

```bash
set -a && source .env && set +a && \
simplismart secrets create \
  --org-id "$ORG_ID" \
  --name "hf-token" \
  --secret-type huggingface \
  --data '{"hf_token": "{HF_TOKEN}"}'
```

Important: the data key must be `hf_token`, not `token`. Note the `uuid` from the output — this is `HF_SECRET_UUID` for the next step.

### Step 1b: Compile the model

`--avatar-url` is a required field (display image). Use the HuggingFace logo as a safe default.

For public models:

```bash
simplismart model-repos create-private-compile \
  --name "{DEPLOYMENT_NAME}" \
  --source-type huggingface \
  --source-url "{HF_MODEL_ID}" \
  --model-class "{MODEL_CLASS}" \
  --accelerator-type nvidia-h100 \
  --avatar-url "https://huggingface.co/front/assets/huggingface_logo-noborder.svg" \
  --org-id "$ORG_ID"
```

For gated models, add `--source-secret`:

```bash
simplismart model-repos create-private-compile \
  --name "{DEPLOYMENT_NAME}" \
  --source-type huggingface \
  --source-url "{HF_MODEL_ID}" \
  --model-class "{MODEL_CLASS}" \
  --accelerator-type nvidia-h100 \
  --avatar-url "https://huggingface.co/front/assets/huggingface_logo-noborder.svg" \
  --source-secret {HF_SECRET_UUID} \
  --org-id "$ORG_ID"
```

Note the `uuid` from the output — this is `MODEL_REPO_UUID`.

### Step 2: Poll compilation status

Terminal states are `SUCCESS`, `FAILED`, `FAILED_OPTIMISING`, `FAILED_LAUNCHING`, and `ERROR`. The poll loop must handle all of them:

```bash
while true; do
  STATUS=$(simplismart model-repos list --name "{DEPLOYMENT_NAME}" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['results'][0]['status'])")
  echo "$(date '+%H:%M:%S') — $STATUS"
  case "$STATUS" in
    SUCCESS) echo "Compilation succeeded."; break ;;
    FAILED*|ERROR) echo "Compilation failed: $STATUS"; exit 1 ;;
  esac
  sleep 30
done
```

Expected status progression: `PENDING` → `LAUNCHING_RAY_CLUSTER` → `OPTIMISING` → `SUCCESS`

### Step 3: Write the autoscale config

```bash
cat > /tmp/autoscale.json << 'EOF'
{"targets": [{"metric": "gpu", "target": {AUTOSCALE_TARGET}}]}
EOF
```

### Step 4: Create the deployment

```bash
simplismart deployments create-private \
  --model-repo {MODEL_REPO_UUID} \
  --org "$ORG_ID" \
  --gpu-id nvidia-h100 \
  --name "{DEPLOYMENT_NAME}" \
  --min-pod-replicas {MIN_REPLICAS} \
  --max-pod-replicas {MAX_REPLICAS} \
  --autoscale-config @/tmp/autoscale.json
```

Note the `deployment_id` from the output.

### Step 5: Health check

```bash
simplismart deployments health --deployment-id {DEPLOYMENT_UUID}
```

After completion, report to the user:
- Endpoint URL
- Deployment UUID (for future operations)
- Health status

---

## Workflow 2 — Check Deployment Status

**Trigger:** User says "status", "list deployments", "is [name] healthy"

List all deployments (the CLI infers org from the token — `--org-id` is not supported here):

```bash
simplismart deployments list
```

Health check for a specific deployment:

```bash
simplismart deployments health --deployment-id {DEPLOYMENT_UUID}
```

Get full details for a specific deployment:

```bash
simplismart deployments get --deployment-id {DEPLOYMENT_UUID}
```

---

## Workflow 3 — Scale a Deployment

**Trigger:** User says "scale [name]", "increase replicas", "prepare for batch job"

Ask for:
1. Deployment UUID (or list deployments to find it)
2. New min replicas
3. New max replicas

```bash
simplismart deployments scale \
  --deployment-id {DEPLOYMENT_UUID} \
  --min-replicas {MIN_REPLICAS} \
  --max-replicas {MAX_REPLICAS}
```

Common patterns to suggest:
- **Before a batch job:** `--min-replicas 4 --max-replicas 16`
- **After a batch job / off-hours:** `--min-replicas 1 --max-replicas 4`
- **High-traffic production:** `--min-replicas 2 --max-replicas 8`

---

## Workflow 4 — Manage Registry Secrets

**Trigger:** User says "add Docker Hub credentials", "store HuggingFace token", "store NVIDIA NIM token", "create secret"

Ask for the secret type: `docker_hub`, `depot`, `nvidia_nim`, or `huggingface`.

Use individual CLI flags — `--payload @file` is not supported by the secrets command:

```bash
# HuggingFace
simplismart secrets create \
  --org-id "$ORG_ID" \
  --name "{SECRET_NAME}" \
  --secret-type huggingface \
  --data '{"hf_token": "{HF_TOKEN}"}'

# Docker Hub
simplismart secrets create \
  --org-id "$ORG_ID" \
  --name "{SECRET_NAME}" \
  --secret-type docker_hub \
  --data '{"username": "{DOCKER_USERNAME}", "token": "{DOCKER_TOKEN}"}'
```

Note the `uuid` from the output — referenced when creating model repos that need registry auth or gated HF access.

List existing secrets (org inferred from token):

```bash
simplismart secrets list
```

---

## Workflow 5 — Stop or Delete a Deployment

**Trigger:** User says "stop [name]", "tear down", "delete deployment"

Always confirm before deleting:

> "This will permanently delete deployment `{name}` (`{uuid}`). Confirm? (yes/no)"

Stop (preserves the deployment config, pauses GPU billing):

```bash
simplismart deployments stop --deployment-id {DEPLOYMENT_UUID}
```

Start a stopped deployment:

```bash
simplismart deployments start --deployment-id {DEPLOYMENT_UUID}
```

Delete deployment (permanent):

```bash
simplismart deployments delete --deployment-id {DEPLOYMENT_UUID}
```

Delete model repo (use `--model-id`, not `--model-repo-id`):

```bash
simplismart model-repos delete --model-id {MODEL_REPO_UUID}
```

---

## Error Handling

| Error | Likely cause | Fix |
|---|---|---|
| `401 Unauthorized` | Invalid or expired PG token | Regenerate at app.simplismart.ai/settings |
| `404 Not Found` on model repo | UUID mismatch or wrong org | Run `simplismart model-repos list` to verify |
| `--avatar-url` required error | Missing required field on compile | Add `--avatar-url "https://huggingface.co/front/assets/huggingface_logo-noborder.svg"` |
| `FAILED_OPTIMISING` | HF license not accepted, missing HF token secret, or bad model class | **First:** confirm the user accepted the model license on HuggingFace. **Then:** verify `--source-secret` is passed with correct UUID. **Then:** verify `model_class` against HF `config.json` |
| `FAILED` / `FAILED_LAUNCHING` / `ERROR` | Bad config or infra error | Check `model_class`; retry; escalate if persistent |
| Compilation stuck in `LAUNCHING_RAY_CLUSTER` | Infrastructure cold start | Wait up to 10 min; escalate if longer |
| `--model-id` not recognised on delete | Wrong flag name | Use `simplismart model-repos delete --model-id {UUID}` |
| CLI command not found | SDK not installed | `pip install simplismart-sdk` |
| `--version` not recognised | CLI does not support that flag | Use `simplismart --help` to verify install |
| `unrecognized arguments: --org-id` on list commands | `deployments list`, `secrets list`, and `model-repos list` infer org from the token | Drop `--org-id`; only `create`/`compile` commands accept it |

---

## Reference

- CLI docs: https://docs.simplismart.ai/sdk/python/cli
- SDK reference: https://docs.simplismart.ai/sdk/python/sdk-reference
- Examples: https://docs.simplismart.ai/sdk/python/examples
- Token: https://app.simplismart.ai/settings?tab=2
