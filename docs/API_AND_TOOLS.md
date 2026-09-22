# 🛠️ Otical FitGuide AI - Tools & API Reference

This document provides a complete catalog of all tools implemented in **Otical FitGuide AI** (`app/agent.py`), detailing parameter signatures, execution logic, and integrated cloud services.

---

## 🧰 Tool Catalog Overview

| Tool Name | Scope / Purpose | Cloud / External Backend |
| :--- | :--- | :--- |
| `PreloadMemoryTool` | Preloads user memory bank context | Vertex AI Memory Bank |
| `get_workout_routine` | Generates structured workout splits | Internal Domain Logic |
| `calculate_heart_rate_zones` | Calculates Karvonen HR training zones | Vertex AI Sandbox Code Executor |
| `calculate_fitness_metrics` | Calculates 1RM, calories burned, or HR zones | Vertex AI Sandbox Code Executor |
| `log_workout` | Logs completed workout sessions | Cloud Firestore (`user_workout_logs`) |
| `search_workout_catalog` | Searches catalog routines | Cloud Firestore (`workout_catalog`) |
| `add_workout_to_catalog` | Saves new workout routines | Cloud Firestore (`workout_catalog`) |
| `upload_workout_media` | Uploads workout guides & text media | Cloud Storage (`fitguide-ai-media-b8f9ab32`) |
| `fetch_wger_exercises` | Queries real exercise database | WGER Public REST API |
| `geocode_address` | Converts addresses to Lat/Long | Google Maps Geocoding API |
| `find_nearby_places` | Locates nearby gyms & parks | Google Maps Places API |
| `query_herbal_rag_corpus` | Queries herbal remedies & recovery lore | Vertex AI RAG Corpus Engine |
| `generate_fitness_item_image` | Generates exercise diagrams / images | Vertex AI GenAI SDK (Imagen) |
| `generate_fitness_item_video` | Generates exercise motion videos | Vertex AI Omni Model (`gemini-omni-flash-preview`) |

---

## 📖 Detailed Tool Specifications

### 1. `get_workout_routine`
- **Description**: Returns recommended exercise splits based on target fitness goals and experience levels.
- **Parameters**:
  - `goal` (*str*): Target objective (e.g., `'strength'`, `'endurance'`, `'core'`).
  - `level` (*str*, default `'beginner'`): Experience level (`'beginner'`, `'intermediate'`, `'advanced'`).
- **Returns**: Formatted breakdown of exercises, sets, reps, and target muscle groups.

---

### 2. `calculate_fitness_metrics`
- **Description**: Evaluates key performance metrics using Python calculation logic.
- **Parameters**:
  - `metric_type` (*str*): Type of calculation (`'1rm'`, `'calories'`, `'hr_zones'`).
  - `weight_kg` (*float*, default `70.0`): User body weight in kg.
  - `age` (*int*, default `30`): User age in years.
  - `resting_hr` (*int*, default `60`): Resting heart rate in bpm.
  - `weight_lifted_kg` (*float*, default `0.0`): Weight lifted for 1RM.
  - `reps` (*int*, default `0`): Repetitions completed.
  - `duration_minutes` (*float*, default `30.0`): Activity duration.
- **Returns**: Formatted metric calculations and recommended training percentages.

---

### 3. `log_workout`
- **Description**: Persists completed workout sessions to Firestore database.
- **Parameters**:
  - `workout_name` (*str*): Name of activity performed.
  - `duration_minutes` (*int*): Session duration in minutes.
  - `intensity` (*str*, default `'moderate'`): Intensity level (`'light'`, `'moderate'`, `'high'`).
  - `notes` (*str*, default `""`): Optional observations or comments.
- **Returns**: Confirmation string with session log document ID and timestamp.

---

### 4. `query_herbal_rag_corpus`
- **Description**: Searches Nicholas Culpeper's *The Complete Herbal* RAG Corpus for natural herbal remedies and plant lore.
- **Parameters**:
  - `query` (*str*): Natural language topic or plant query (e.g., `'chamomile for muscle recovery'`).
- **Returns**: Relevant text snippets retrieved from the RAG Corpus.

---

### 5. `generate_fitness_item_image`
- **Description**: Generates exercise visual diagrams using Vertex AI Imagen models in the `global` region.
- **Parameters**:
  - `prompt` (*str*): Description of the fitness item or exercise form to visualize.
  - `tool_context` (*ToolContext*): Injected ADK Tool Context.
- **Returns**: Public HTTPS URL of the stored Cloud Storage image.

---

### 6. `generate_fitness_item_video`
- **Description**: Generates short exercise motion videos using Google's Omni model (`gemini-omni-flash-preview`) in the `global` region.
- **Parameters**:
  - `prompt` (*str*): Description of the workout exercise or form animation.
  - `tool_context` (*ToolContext*): Injected ADK Tool Context.
- **Returns**: Public HTTPS URL of the stored Cloud Storage video file.
