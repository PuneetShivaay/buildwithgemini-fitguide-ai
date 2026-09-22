# 📖 Otical FitGuide AI - Build Journey & Design Rationale

This document provides a comprehensive step-by-step account of how **Otical FitGuide AI** was designed, built, and deployed, explaining the architectural decisions and design rationale behind every single component.

---

## 🎯 1. Project Scaffolding & Framework Selection

### **What We Built**:
- A fitness coaching agentic application scaffolded using Google's **Agent Development Kit (ADK)** and deployed to **Vertex AI Agent Engine**.
- Root Agent (`root_agent`) powered by **`gemini-2.5-flash`**.

### **Why We Made These Choices**:
- **Google ADK Framework**: Standardizes multi-tool agent orchestration, callback interceptors, state management, and seamless deployment to Vertex AI Agent Runtime.
- **`gemini-2.5-flash`**: Selected for its exceptional reasoning speed, native multi-tool call handling, low latency, and 1M token context window.

---

## 🧠 2. Cross-Session Memory Architecture

### **What We Built**:
- Integrated `VertexAiMemoryBankService` with `PreloadMemoryTool` and `generate_memories_callback`.

### **Why We Made These Choices**:
- **The Problem**: A personal fitness coach is useless if it forgets user injuries, dietary restrictions, body weight, or training history between chat sessions.
- **The Solution**: Memory Bank automatically preloads user context at the start of a turn and persists finished conversation memories into Vertex AI Memory Bank, ensuring personalized coaching over time without redundant user prompts.

---

## ⚡ 3. Safe Math via Sandbox Code Execution

### **What We Built**:
- `AgentEngineSandboxCodeExecutor` running Python calculations for 1RM (One-Rep Max), Target Heart Rate (THR) Karvonen zones, and caloric expenditure.

### **Why We Made These Choices**:
- **The Problem**: Large Language Models (LLMs) are notorious for arithmetic hallucinations when computing complex equations.
- **The Solution**: Routing calculations to an isolated Python Sandbox environment guarantees 100% deterministic mathematical accuracy for safety-critical physical metrics:
  $$\text{1RM} = w \times \left(1 + \frac{r}{30}\right)$$
  $$\text{THR} = \text{HR}_{\text{rest}} + (\text{HR}_{\text{max}} - \text{HR}_{\text{rest}}) \times \%\text{Target}$$

---

## 💾 4. Database Persistence & Cloud Storage

### **What We Built**:
- **Google Cloud Firestore**:
  - `user_workout_logs`: Records completed sessions (duration, intensity, notes, timestamps).
  - `workout_catalog`: Standardized exercise routines filtered by fitness goals and difficulty levels.
- **Google Cloud Storage (GCS)** (`fitguide-ai-media-b8f9ab32`):
  - Holds public exercise form guides, generated posture images, and motion video bytes.

### **Why We Made These Choices**:
- **Firestore**: Provides schema-less NoSQL flexibility, instant queries, and scalable storage for real-time application logging.
- **Cloud Storage Bucket**: Offers reliable public HTTPS URLs (`https://storage.googleapis.com/<bucket>/<object>`) for serving media assets to the web interface.

---

## 🎨 5. Multimodal Image & Video Generation

### **What We Built**:
- `generate_fitness_item_image`: Generates exercise posture diagrams using **Vertex AI Imagen** in the `global` region.
- `generate_fitness_item_video`: Generates short motion clips using Google's **Omni model (`gemini-omni-flash-preview`)** in the `global` region.

### **Why We Made These Choices**:
- **Visual Learning**: Fitness guidance is inherently visual. Plain text descriptions of exercises (like kettlebell swings or squats) are often insufficient or misunderstood.
- **Dual Output Strategy**:
  1. `tool_context.save_artifact`: Displays generated media inline inside the ADK Playground Artifacts panel.
  2. Cloud Storage upload: Returns a permanent public HTTPS URL for web frontend rendering.

---

## 🌿 6. Herbal Recovery Lore via Vector RAG

### **What We Built**:
- `query_herbal_rag_corpus`: Queries a dedicated Vertex AI RAG Corpus indexing Nicholas Culpeper's *The Complete Herbal*.

### **Why We Made These Choices**:
- **Grounding & Lore**: Grounding recovery recommendations (e.g., chamomile, arnica, or willow bark for post-workout muscle soreness) in verified historical text prevents hallucination and adds domain depth.

---

## 📱 7. Adaptive UI (A2UI) & Web Frontend Rebranding

### **What We Built**:
- **A2UI Schema Manager (v0.8)**: Transforms structured JSON payloads into native UI components (`Card`, `Column`, `Row`, `Text`, `Image`).
- **Web Interface Rebranding**:
  - App Header: **Otical FitGuide AI - Personal Fitness Coach**
  - Prompt Chips: 3 one-click prompt buttons (`🏃 3-Day Workout Plan`, `❤️ Heart Rate Zones`, `🎨 Kettlebell Swing Visual`).
  - Dialogue Layout: Styled user (`👤`) and coach (`🏋️`) avatars with smooth message fade-in animations.
  - Footer Links: Hyperlinked Otical & Guruphoria credits (hidden in UI via HTML comment as requested).

### **Why We Made These Choices**:
- **Enhanced UX**: A modern AI app must feel dynamic and interactive. A2UI replaces long blocks of text with interactive cards, while prompt chips lower user friction for initial interaction.

---

## 🎥 8. Automated Verification, Recording & Documentation

### **What We Built**:
- Playwright E2E recording script (`record-demo`) producing `fitguide_agent_demo.webm`.
- Converted looping GIF (`demo.gif`) embedded in `README.md`.
- Complete documentation suite (`ARCHITECTURE.md`, `API_AND_TOOLS.md`, `DEPLOYMENT_GUIDE.md`, `BUILD_JOURNEY_AND_RATIONALE.md`).

### **Why We Made These Choices**:
- **Verifiable Excellence**: Competition reviewers and gallery visitors need immediate visual proof of working functionality without building from source.
- **Transparency**: Storing both `demo.gif` (for web README preview) and `assets/fitguide_agent_demo.webm` (for full HD video inspection) ensures complete transparency.
