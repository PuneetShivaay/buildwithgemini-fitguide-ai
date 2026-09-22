# 🏗️ Otical FitGuide AI - Code Architecture

This document provides a detailed overview of the system architecture, component layout, data flow, and Google Cloud platform integrations powering **Otical FitGuide AI**.

---

## 📐 System Architecture Diagram

```mermaid
flowchart TD
    User([👤 User / Browser]) <-->|HTTP / HTML / A2UI| Frontend[🌐 FastAPI Frontend Proxy<br/>frontend/main.py]
    Frontend <-->|A2A / HTTP Protocol| AgentEngine[🧠 Vertex AI Agent Engine<br/>projects/.../reasoningEngines/...]

    subgraph AgentEngineSub ["ADK Root Agent (app/agent.py)"]
        Agent[Agent: root_agent<br/>Model: gemini-2.5-flash]
        A2UIParser[A2UI Callback<br/>app/a2ui_utils.py]
        Sandbox[Vertex AI Sandbox Code Executor<br/>Python Runtime]
    end

    AgentEngine <--> AgentEngineSub

    subgraph GCP ["Google Cloud Services & External Integration"]
        MemoryBank[(🧠 Vertex AI Memory Bank<br/>Cross-session User Context)]
        Firestore[(💾 Cloud Firestore<br/>user_workout_logs & workout_catalog)]
        GCS[(☁️ Cloud Storage<br/>fitguide-ai-media-b8f9ab32)]
        RAGCorpus[(🌿 Vertex AI RAG Corpus<br/>Culpeper Herbal Lore)]
        GenAI[🎨 Google GenAI SDK<br/>Imagen & gemini-omni-flash-preview]
        ExternalAPIs[🌐 External APIs<br/>WGER REST & Google Maps]
    end

    Agent <-->|Preload & Save| MemoryBank
    Agent <-->|Logs & Catalog| Firestore
    Agent -->|Media Uploads| GCS
    Agent <-->|Vector Retrieval| RAGCorpus
    Agent <-->|Multimodal Gen| GenAI
    Agent <-->|REST Calls| ExternalAPIs
    Agent <-->|Math Exec| Sandbox
```

---

## 🧩 Core Architectural Components

### 1. **ADK Root Agent (`app/agent.py`)**
- Built using **Google Agent Development Kit (ADK)**.
- **Model**: Powered by `gemini-2.5-flash` with automatic HTTP retry options.
- **System Prompt**: Generated via `A2uiSchemaManager` (v0.8) instructing the agent on dietary/allergy safety, workout planning, and structured A2UI surface rendering.

### 2. **State & Memory Management (`VertexAiMemoryBankService`)**
- Stores long-term memory across sessions.
- Injects user allergies, health restrictions, and past workout performance into context via `PreloadMemoryTool`.
- Automatically persists finished chat sessions back to Vertex AI Memory Bank via `generate_memories_callback`.

### 3. **Adaptive UI Engine (`app/a2ui_utils.py`)**
- Utilizes `A2uiSchemaManager` and `BasicCatalog`.
- Transforms raw JSON data structures into flat, accessible UI components (`Card`, `Column`, `Row`, `Text`, `Image`).
- `a2ui_callback` interceptor extracts structured data parts without leaking raw code blocks.

### 4. **Isolated Code Execution (`AgentEngineSandboxCodeExecutor`)**
- Safe, sandboxed Python code execution environment for complex mathematical formulas:
  - Epley 1RM formula: $1RM = W \times (1 + \frac{r}{30})$
  - Karvonen Heart Rate Reserve: $THR = HR_{rest} + (HR_{max} - HR_{rest}) \times \%Target$
  - Metabolic Equivalent of Task (MET) calorie burn calculations.

### 5. **Multimodal Visual & Video Generation**
- **Imagen Visuals**: Generates exercise form illustrations using `gemini-3.1-flash-lite-image` in the `global` region.
- **Omni Exercise Videos**: Generates short motion clips using `gemini-omni-flash-preview` in the `global` region.
- **Dual Pipeline**:
  1. Saves inline byte artifacts to the ADK Playground Artifacts panel (`tool_context.save_artifact`).
  2. Uploads public HTTPS objects directly to Google Cloud Storage (`fitguide-ai-media-b8f9ab32`).

---

## 🔄 Interaction Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as FastAPI Frontend
    participant Agent as ADK Root Agent
    participant Tools as Tool Execution Layer
    participant GCP as Google Cloud (Firestore/Memory/GenAI)

    User->>Frontend: Send prompt e.g., "Calculate 1RM & log workout"
    Frontend->>Agent: POST /chat (A2A Message)
    Agent->>Tools: Invoke PreloadMemoryTool
    Tools->>GCP: Fetch Memory Bank context
    GCP-->>Agent: User preferences & allergies
    Agent->>Tools: Call calculate_fitness_metrics & log_workout
    Tools->>GCP: Execute calculation & insert Firestore log
    GCP-->>Tools: Confirmation & Log Document ID
    Tools-->>Agent: Tool execution result
    Agent->>Agent: Format output with A2UI JSON surface
    Agent-->>Frontend: Structured A2UI payload + response
    Frontend-->>User: Render avatar dialogue bubble & card UI
```
