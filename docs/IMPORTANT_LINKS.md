# 🔗 Otical FitGuide AI - Important Links & Resources Directory

This document serves as a central index of all live service endpoints, GCP management consoles, repository assets, developer reference guides, and resource IDs for **Otical FitGuide AI**.

---

## 🌐 1. Live Application & Public Endpoints

| Resource | Description | URL / Link |
| :--- | :--- | :--- |
| **Live Web App** | Primary Cloud Run Frontend URL | [https://fitguide-frontend-mmnnp72rna-uc.a.run.app](https://fitguide-frontend-mmnnp72rna-uc.a.run.app) |
| **Cloud Run Service URL** | Alternative Cloud Run URL | [https://fitguide-frontend-461062469766.us-central1.run.app](https://fitguide-frontend-461062469766.us-central1.run.app) |
| **Media Bucket (GCS)** | Public Storage Bucket for Images & Videos | [https://storage.googleapis.com/fitguide-ai-media-b8f9ab32](https://storage.googleapis.com/fitguide-ai-media-b8f9ab32) |
| **Agent Card JSON** | A2A Protocol Agent Card Discovery endpoint | [https://us-east1-aiplatform.googleapis.com/reasoningEngines/v1/projects/461062469766/locations/us-east1/reasoningEngines/5478956601161285632/api/a2a/app/.well-known/agent-card.json](https://us-east1-aiplatform.googleapis.com/reasoningEngines/v1/projects/461062469766/locations/us-east1/reasoningEngines/5478956601161285632/api/a2a/app/.well-known/agent-card.json) |

---

## 📦 2. GitHub Repository & Showcase Media

| Resource | Description | URL / Link |
| :--- | :--- | :--- |
| **Public GitHub Repo** | Source Code & Documentation | [https://github.com/PuneetShivaay/buildwithgemini-fitguide-ai](https://github.com/PuneetShivaay/buildwithgemini-fitguide-ai) |
| **Full WebM Demo Video** | 1080p HD Video Recording (`assets/`) | [fitguide_agent_demo.webm](https://github.com/PuneetShivaay/buildwithgemini-fitguide-ai/blob/main/assets/fitguide_agent_demo.webm) |
| **Animated GIF Demo** | Looping Preview GIF (`demo.gif`) | [demo.gif](https://github.com/PuneetShivaay/buildwithgemini-fitguide-ai/blob/main/demo.gif) |
| **Swag Submission Form** | Official Pre-filled Competition Entry Form | [Google Submission Form](https://docs.google.com/forms/d/e/1FAIpQLSfvbIUMrHLf2iUYVgQkr981unQwuLdigLB7yJp3VdtYH85Dzw/viewform?usp=pp_url&entry.896374137=https%3A%2F%2Fgithub.com%2FPuneetShivaay%2Fbuildwithgemini-fitguide-ai) |

---

## ☁️ 3. Google Cloud Console Management Links

| Console Service | Purpose | Console Link |
| :--- | :--- | :--- |
| **Vertex AI Agent Engine** | View reasoning engine instance & logs | [Agent Engine Console](https://console.cloud.google.com/vertex-ai/agents/agent-engines/locations/us-east1/agent-engines/5478956601161285632?project=qwiklabs-gcp-01-b8f9ab327387) |
| **Cloud Run Console** | View frontend proxy metrics & logs | [Cloud Run Console](https://console.cloud.google.com/run/detail/us-central1/fitguide-frontend/metrics?project=qwiklabs-gcp-01-b8f9ab327387) |
| **Cloud Firestore** | Inspect `user_workout_logs` & `workout_catalog` | [Firestore Data Console](https://console.cloud.google.com/firestore/databases/-default-/data/panel/user_workout_logs?project=qwiklabs-gcp-01-b8f9ab327387) |
| **Cloud Storage** | Inspect `fitguide-ai-media-b8f9ab32` bucket | [GCS Bucket Console](https://console.cloud.google.com/storage/browser/fitguide-ai-media-b8f9ab32?project=qwiklabs-gcp-01-b8f9ab327387) |

---

## 📚 4. Documentation & Developer Reference Links

| Document / Guide | Description | URL / Link |
| :--- | :--- | :--- |
| **Build with Gemini Guide** | Official Track 3 Interactive Lab Guide | [https://storage.googleapis.com/bwg-track3-demo-guide/GSI/index.html](https://storage.googleapis.com/bwg-track3-demo-guide/GSI/index.html) |
| **Otical Site** | Developer Portfolio Site | [https://otical.vercel.app/](https://otical.vercel.app/) |
| **Guruphoria Site** | Developer Portfolio Site | [https://guruphoria.netlify.app/](https://guruphoria.netlify.app/) |
| **WGER Exercise API** | Public REST API for exercise database | [https://wger.de/en/software/api](https://wger.de/en/software/api) |
| **Google ADK Docs** | Agent Development Kit Documentation | [https://google-genai.github.io/adk/](https://google-genai.github.io/adk/) |

---

## 🔑 5. Static Developer Resource Identifiers

```ini
GCP_PROJECT_ID = "qwiklabs-gcp-01-b8f9ab327387"
GCP_PROJECT_NUMBER = "461062469766"
AGENT_ENGINE_RESOURCE_NAME = "projects/461062469766/locations/us-east1/reasoningEngines/5478956601161285632"
GCS_MEDIA_BUCKET = "fitguide-ai-media-b8f9ab32"
HERBAL_RAG_CORPUS_ID = "projects/461062469766/locations/us-central1/ragCorpora/7625807986064424960"
SERVICE_ACCOUNT = "service-461062469766@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
```
