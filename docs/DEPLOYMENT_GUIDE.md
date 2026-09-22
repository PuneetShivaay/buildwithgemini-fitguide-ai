# 🚀 Otical FitGuide AI - Deployment Guide

This guide provides step-by-step instructions for deploying **Otical FitGuide AI** to Google Cloud Platform using `agents-cli` for the backend agent and Google Cloud Run for the web frontend.

---

## 📋 Prerequisites

1. **Google Cloud SDK (`gcloud`)** installed and authenticated:
   ```bash
   gcloud auth login
   gcloud config set project <YOUR_GCP_PROJECT_ID>
   ```
2. **Required GCP IAM Roles**:
   - `roles/aiplatform.user`
   - `roles/datastore.user`
   - `roles/storage.objectAdmin`
   - `roles/run.admin`

---

## 🧠 1. Deploy Agent to Vertex AI Agent Engine

Using `agents-cli`, deploy the agent codebase in `app/` to Agent Engine (`agent_runtime`):

```bash
agents-cli scaffold deploy \
  --manifest-file agents-cli-manifest.yaml \
  --deployment-target agent_runtime
```

Upon successful deployment, `deployment_metadata.json` will be updated with your `AGENT_ENGINE_RESOURCE_NAME`:
```json
{
  "resource_name": "projects/<PROJECT_ID>/locations/us-central1/reasoningEngines/<ENGINE_ID>"
}
```

---

## 🔑 2. Service Account Permissions

Grant the deployed agent's service account access to Firestore and Cloud Storage:

```bash
AGENT_SA=$(gcloud reasoning-engines describe <ENGINE_ID> --location=us-central1 --format="value(serviceAccount)")

# Firestore Access
gcloud projects add-iam-policy-binding <YOUR_GCP_PROJECT_ID> \
  --member="serviceAccount:${AGENT_SA}" \
  --role="roles/datastore.user"

# GCS Storage Admin
gcloud storage buckets add-iam-policy-binding gs://fitguide-ai-media-b8f9ab32 \
  --member="serviceAccount:${AGENT_SA}" \
  --role="roles/storage.objectAdmin"
```

---

## 🌐 3. Deploy Frontend to Google Cloud Run

Deploy the FastAPI proxy frontend (`frontend/`) to Cloud Run:

```bash
gcloud run deploy fitguide-frontend \
  --source ./frontend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/us-central1/reasoningEngines/<ENGINE_ID>",AGENT_DIRECTORY="app"
```

Grant the Cloud Run default service account permission to call Vertex AI Agent Engine:

```bash
PROJECT_NUMBER=$(gcloud projects describe <YOUR_GCP_PROJECT_ID> --format="value(projectNumber)")

gcloud projects add-iam-policy-binding <YOUR_GCP_PROJECT_ID> \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```
