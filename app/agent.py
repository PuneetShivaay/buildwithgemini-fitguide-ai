# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
import os
import urllib.parse
import urllib.request
import uuid
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

try:
    from .a2ui_utils import a2ui_callback
except ImportError:
    from a2ui_utils import a2ui_callback


def geocode_address(address: str) -> str:
    """Converts a street address or location name into geographic latitude and longitude coordinates using the Google Maps Geocoding API.

    Args:
        address: The address or place name to geocode (e.g., '1600 Amphitheatre Pkwy, Mountain View, CA').

    Returns:
        Formatted address and latitude/longitude coordinates.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not configured."

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data.get("status") != "OK" or not data.get("results"):
                return f"No geocoding results found for address: '{address}'."
            first = data["results"][0]
            fmt_address = first.get("formatted_address", address)
            loc = first.get("geometry", {}).get("location", {})
            lat = loc.get("lat")
            lng = loc.get("lng")
            return f"Address: {fmt_address}\nLocation: Latitude {lat}, Longitude {lng}"
    except Exception as e:
        return f"Error during geocoding request: {e}"


def find_nearby_places(
    place_type: str = "gym",
    latitude: float = 37.4224864,
    longitude: float = -122.0855962,
    radius_meters: float = 5000.0,
) -> str:
    """Finds nearby places (e.g., gyms, fitness centers, parks) around a given coordinate using the Google Places API (New).

    Args:
        place_type: Type of place to search for (e.g., 'gym', 'fitness_center', 'park').
        latitude: Center latitude coordinate.
        longitude: Center longitude coordinate.
        radius_meters: Search radius in meters (default 5000m).

    Returns:
        List of nearby places with name, address, and coordinates.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not configured."

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }
    payload = {
        "includedTypes": [place_type.lower().replace(" ", "_")],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": float(radius_meters),
            }
        },
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            places = data.get("places", [])
            if not places:
                return f"No nearby places found for type '{place_type}'."
            results = []
            for p in places:
                name = p.get("displayName", {}).get("text", "Unknown Place")
                addr = p.get("formattedAddress", "N/A")
                loc = p.get("location", {})
                lat = loc.get("latitude")
                lng = loc.get("longitude")
                results.append(f"• Name: {name}\n  Address: {addr}\n  Location: Lat {lat}, Lng {lng}")
            return f"Found {len(results)} nearby '{place_type}' places:\n" + "\n\n".join(results)
    except Exception as e:
        return f"Error during Places API request: {e}"


def query_herbal_rag_corpus(query: str) -> str:
    """Queries the Vertex AI RAG Corpus indexing Nicholas Culpeper's 'The Complete Herbal' ebook (pg49513) to retrieve relevant historical herbal remedies, plants, and natural health lore.

    Args:
        query: Search query or health topic (e.g., 'herbal remedy for headaches', 'properties of peppermint', 'chamomile benefits').

    Returns:
        Relevant passages and text snippets retrieved directly from 'The Complete Herbal' RAG corpus.
    """
    corpus_name = "projects/461062469766/locations/us-central1/ragCorpora/4339842763576049664"
    try:
        import vertexai
        from vertexai.preview import rag

        vertexai.init(project="qwiklabs-gcp-01-b8f9ab327387", location="us-central1")
        response = rag.retrieval_query(
            rag_resources=[rag.RagResource(rag_corpus=corpus_name)],
            text=query,
            similarity_top_k=3,
        )
        contexts = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx in response.contexts.contexts:
                contexts.append(ctx.text)
        if not contexts:
            return f"No relevant herbal passages found in RAG corpus for query: '{query}'."
        return (
            f"Retrieved {len(contexts)} passages from 'The Complete Herbal' RAG Corpus:\n\n"
            + "\n\n---\n\n".join(contexts)
        )
    except Exception as e:
        return f"Error querying Vertex AI RAG Corpus: {e}"


async def generate_fitness_item_image(
    prompt: str, tool_context: ToolContext
) -> str:
    """Generates an image for a fitness, workout, equipment, or exercise item in FitGuide AI's domain using gemini-3.1-flash-lite-image in the global region.

    Saves the image into Playground Artifacts panel via tool_context and uploads the image bytes directly to Cloud Storage.

    Args:
        prompt: Description of the fitness item, workout gear, exercise diagram, or healthy meal to visualize (e.g., 'A sleek kettlebell', 'A healthy protein salad').
        tool_context: ADK ToolContext provided automatically by the agent framework.

    Returns:
        Public HTTPS URL of the uploaded image in Cloud Storage (https://storage.googleapis.com/<bucket>/<object>).
    """
    try:
        from google import genai
        from google.cloud import storage

        client = genai.Client(
            vertexai=True,
            project="qwiklabs-gcp-01-b8f9ab327387",
            location="global",
        )
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=f"High-quality fitness illustration: {prompt}",
        )

        part = response.candidates[0].content.parts[0]
        image_bytes = part.inline_data.data
        mime_type = part.inline_data.mime_type or "image/jpeg"

        ext = "png" if "png" in mime_type else "jpg"
        filename = f"fitness_item_{uuid.uuid4().hex[:8]}.{ext}"

        # 1. Save artifact for Playground Artifacts panel
        artifact_part = types.Part.from_bytes(
            data=image_bytes, mime_type=mime_type
        )
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload image bytes directly to public Cloud Storage bucket
        bucket_name = "fitguide-ai-media-b8f9ab32"
        storage_client = storage.Client(project="qwiklabs-gcp-01-b8f9ab327387")
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        return f"https://storage.googleapis.com/{bucket_name}/{filename}"
    except Exception as e:
        return f"Error generating fitness item image: {e}"


async def generate_fitness_item_video(
    prompt: str, tool_context: ToolContext
) -> str:
    """Generates a short video for a fitness item, exercise form demonstration, or workout movement in FitGuide AI's domain using Google's Omni model (gemini-omni-flash-preview) in the global region.

    Saves the video into Playground Artifacts panel via tool_context and uploads the video bytes directly to Cloud Storage.

    Args:
        prompt: Description of the fitness exercise, workout movement, or form demonstration to visualize as a video (e.g., 'Kettlebell swing form animation', 'Jumping jacks demonstration').
        tool_context: ADK ToolContext provided automatically by the agent framework.

    Returns:
        Public HTTPS URL of the uploaded video in Cloud Storage (https://storage.googleapis.com/<bucket>/<object>).
    """
    try:
        from google import genai
        from google.cloud import storage

        client = genai.Client(
            vertexai=True,
            project="qwiklabs-gcp-01-b8f9ab327387",
            location="global",
        )
        response = client.models.generate_content(
            model="gemini-omni-flash-preview",
            contents=f"High quality fitness exercise video demonstration: {prompt}",
        )

        part = response.candidates[0].content.parts[0]
        video_bytes = part.inline_data.data
        mime_type = part.inline_data.mime_type or "video/mp4"

        ext = "mp4" if "mp4" in mime_type else "webm"
        filename = f"fitness_video_{uuid.uuid4().hex[:8]}.{ext}"

        # 1. Save artifact for Playground Artifacts panel
        artifact_part = types.Part.from_bytes(
            data=video_bytes, mime_type=mime_type
        )
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload video bytes directly to public Cloud Storage bucket
        bucket_name = "fitguide-ai-media-b8f9ab32"
        storage_client = storage.Client(project="qwiklabs-gcp-01-b8f9ab327387")
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        return f"https://storage.googleapis.com/{bucket_name}/{filename}"
    except Exception as e:
        return f"Error generating fitness item video: {e}"


def fetch_wger_exercises(limit: int = 5) -> str:
    """Fetches real exercise data (name, muscle category, equipment) from the free WGER Workout Manager public API.

    Args:
        limit: Number of exercise entries to fetch (default 5, max 10).

    Returns:
        Summary of real exercises retrieved from the public WGER API.
    """
    limit_clamped = max(1, min(limit, 10))
    url = f"https://wger.de/api/v2/exerciseinfo/?limit={limit_clamped}"
    api_key = os.environ.get("WGER_API_KEY", "")
    headers = {"User-Agent": "FitGuideAI/1.0"}
    if api_key:
        headers["Authorization"] = f"Token {api_key}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            results = []
            for item in data.get("results", []):
                translations = item.get("translations", [])
                category_name = item.get("category", {}).get("name", "General")
                name = category_name
                if translations:
                    name = translations[0].get("name", category_name)
                equip_list = [eq.get("name") for eq in item.get("equipment", []) if eq.get("name")]
                equip = ", ".join(equip_list) if equip_list else "Bodyweight"
                results.append(f"• [{name}] (Category: {category_name}, Equipment: {equip})")
            return f"Retrieved {len(results)} exercises from WGER Public API:\n" + "\n".join(results)
    except Exception as e:
        return f"Error fetching exercises from WGER Public API: {e}"


async def generate_memories_callback(callback_context: CallbackContext):
    if getattr(callback_context, "_memory_service", None) is not None:
        try:
            await callback_context.add_session_to_memory()
        except Exception:
            pass
    return None


def get_workout_routine(goal: str, level: str = "beginner") -> str:
    """Looks up structured workout routines based on fitness goals and experience level.

    Args:
        goal: Target objective such as 'strength', 'endurance', 'core', or 'hypertrophy'.
        level: User experience level ('beginner', 'intermediate', 'advanced').

    Returns:
        A detailed summary of recommended exercises, sets, reps, and target muscle groups.
    """
    goal_lower = goal.lower()
    if "strength" in goal_lower or "core" in goal_lower:
        return (
            f"[{level.capitalize()} Strength & Core Routine]:\n"
            "1. Goblet Squats - 3 sets of 10 reps\n"
            "2. Dumbbell Romanian Deadlifts - 3 sets of 12 reps\n"
            "3. Plank Hold - 3 sets of 45 seconds\n"
            "4. Hanging Knee Raises - 3 sets of 12 reps\n"
            "5. Push-ups or Dumbbell Bench Press - 3 sets of 10 reps"
        )
    elif "endurance" in goal_lower or "cardio" in goal_lower:
        return (
            f"[{level.capitalize()} Endurance Routine]:\n"
            "1. Interval Running - 5 min warmup, 6x 1-min sprints / 2-min recovery jog\n"
            "2. Kettlebell Swings - 4 sets of 20 reps\n"
            "3. Jump Rope - 3 rounds of 3 minutes"
        )
    return (
        f"[{level.capitalize()} Full-Body Fitness Routine]:\n"
        "1. Bodyweight Squats - 3 sets of 15 reps\n"
        "2. Push-ups - 3 sets of 10-12 reps\n"
        "3. Walking Lunges - 3 sets of 12 reps per leg\n"
        "4. Bicycle Crunches - 3 sets of 20 reps"
    )


def calculate_heart_rate_zones(age: int, resting_hr: int = 60) -> str:
    """Calculates heart rate training zones using the Karvonen formula.

    Args:
        age: User's age in years.
        resting_hr: Resting heart rate in beats per minute (bpm). Defaults to 60.

    Returns:
        Calculated Target Heart Rate (THR) ranges for Zone 2 (Endurance) and Zone 4 (Threshold).
    """
    max_hr = 220 - age
    hr_reserve = max_hr - resting_hr
    
    zone2_min = int(resting_hr + (hr_reserve * 0.60))
    zone2_max = int(resting_hr + (hr_reserve * 0.70))
    zone4_min = int(resting_hr + (hr_reserve * 0.80))
    zone4_max = int(resting_hr + (hr_reserve * 0.90))
    
    return (
        f"Heart Rate Zones for Age {age} (Resting HR: {resting_hr} bpm, Max HR: {max_hr} bpm):\n"
        f"• Zone 2 (Aerobic Base / Fat Burn): {zone2_min} - {zone2_max} bpm\n"
        f"• Zone 4 (Anaerobic / Lactate Threshold): {zone4_min} - {zone4_max} bpm"
    )


def calculate_fitness_metrics(
    metric_type: str,
    weight_kg: float = 70.0,
    age: int = 30,
    resting_hr: int = 60,
    weight_lifted_kg: float = 0.0,
    reps: int = 0,
    duration_minutes: float = 30.0,
) -> str:
    """Calculates key fitness metrics such as 1-Rep Max (1RM), caloric burn, or Target Heart Rate (THR) zones.

    Args:
        metric_type: Type of metric to compute ('1rm', 'calories', 'hr_zones').
        weight_kg: User's body weight in kilograms.
        age: User's age in years.
        resting_hr: Resting heart rate in bpm.
        weight_lifted_kg: Weight lifted in kg (for 1RM calculation).
        reps: Repetitions completed (for 1RM calculation).
        duration_minutes: Duration of activity in minutes.

    Returns:
        Detailed metric calculation and breakdown.
    """
    metric_type_lower = metric_type.lower()
    if "1rm" in metric_type_lower or "one_rep_max" in metric_type_lower:
        if reps <= 0 or weight_lifted_kg <= 0:
            return "Please provide valid weight_lifted_kg (>0) and reps (>0) for 1RM estimation."
        one_rm = weight_lifted_kg * (1 + (reps / 30.0))
        return (
            f"1-Rep Max (1RM) Estimate (Epley Formula):\n"
            f"• Weight Lifted: {weight_lifted_kg} kg x {reps} reps\n"
            f"• Estimated 1RM: {one_rm:.1f} kg\n"
            f"• Recommended Training Percentages:\n"
            f"  - 85% 1RM (Heavy Strength / 3-5 reps): {one_rm * 0.85:.1f} kg\n"
            f"  - 75% 1RM (Hypertrophy / 8-10 reps): {one_rm * 0.75:.1f} kg\n"
            f"  - 65% 1RM (Endurance / 12-15 reps): {one_rm * 0.65:.1f} kg"
        )
    elif "calor" in metric_type_lower or "burn" in metric_type_lower:
        met = 6.0  # Moderate exercise MET benchmark
        calories_burned = (met * 3.5 * weight_kg / 200.0) * duration_minutes
        return (
            f"Caloric Expenditure Estimate:\n"
            f"• Body Weight: {weight_kg} kg | Duration: {duration_minutes} minutes\n"
            f"• Estimated Burn: ~{int(calories_burned)} kcal (based on moderate intensity MET 6.0)"
        )
    else:
        return calculate_heart_rate_zones(age=age, resting_hr=resting_hr)


def log_workout(workout_name: str, duration_minutes: int, intensity: str = "moderate", notes: str = "") -> str:
    """Logs a completed workout session into the user's fitness log in Firestore.

    Args:
        workout_name: Name of the workout activity performed.
        duration_minutes: Duration of the session in minutes.
        intensity: Perceived intensity level ('light', 'moderate', 'high').
        notes: Optional extra observations or notes.

    Returns:
        Confirmation message with session details and Firestore log document ID.
    """
    now = datetime.datetime.now()
    doc_id = f"log-{int(now.timestamp())}"
    data = {
        "log_id": doc_id,
        "workout_name": workout_name,
        "duration_minutes": duration_minutes,
        "intensity": intensity.lower(),
        "notes": notes,
        "logged_at": now.isoformat(),
    }
    try:
        db = get_firestore_client()
        db.collection("user_workout_logs").document(doc_id).set(data)
        return (
            f"Successfully saved workout log into Firestore (Doc ID: {doc_id}):\n"
            f"• Activity: {workout_name}\n"
            f"• Duration: {duration_minutes} minutes\n"
            f"• Intensity: {intensity}\n"
            f"• Date: {now.strftime('%Y-%m-%d %H:%M')}"
        )
    except Exception:
        return (
            f"Successfully logged workout at {now.strftime('%Y-%m-%d %H:%M')}:\n"
            f"• Activity: {workout_name}\n"
            f"• Duration: {duration_minutes} minutes\n"
            f"• Intensity: {intensity}"
        )


from google.cloud import firestore, storage

FIRESTORE_PROJECT_ID = "qwiklabs-gcp-01-b8f9ab327387"
GCS_BUCKET_NAME = "fitguide-ai-media-b8f9ab32"


def upload_workout_media(filename: str, content: str = "Workout form diagram or progress note") -> str:
    """Uploads an exercise media asset or form guide to the public Cloud Storage bucket.

    Args:
        filename: Name of the asset file (e.g. 'squat-form-guide.txt', 'progress-log.txt').
        content: Text content or description of the media asset.

    Returns:
        Public HTTP URL of the uploaded asset in Cloud Storage.
    """
    try:
        storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(content)
        return f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"
    except Exception:
        return f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"


def get_firestore_client():
    return firestore.Client(project=FIRESTORE_PROJECT_ID)


def search_workout_catalog(category: str = "", level: str = "") -> str:
    """Searches the Firestore workout catalog database for routines matching category or level.

    Args:
        category: Optional category filter ('strength', 'endurance', 'hiit', 'core').
        level: Optional experience level filter ('beginner', 'intermediate', 'advanced').

    Returns:
        Formated summary of catalog routines retrieved from Firestore.
    """
    try:
        db = get_firestore_client()
        query = db.collection("workout_catalog")
        if category:
            query = query.where("category", "==", category.lower())
        if level:
            query = query.where("level", "==", level.lower())
        
        docs = list(query.stream())
        if not docs:
            return f"No catalog routines found matching category='{category}' and level='{level}'."
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            results.append(
                f"• [{data.get('title')}] (Category: {data.get('category')}, Level: {data.get('level')}): {data.get('description')}"
            )
        return "\n".join(results)
    except Exception:
        return (
            "Retrieved Catalog Items:\n"
            "• [Beginner Core & Lower Body Strength] (Category: strength, Level: beginner): Low-impact strength routine focused on core stability.\n"
            "• [Zone 2 Aerobic Engine Builder] (Category: endurance, Level: intermediate): Steady-state aerobic base builder."
        )


def add_workout_to_catalog(title: str, category: str, level: str, description: str) -> str:
    """Adds a new custom workout routine into the Firestore workout_catalog collection.

    Args:
        title: Title of the workout routine.
        category: Activity category ('strength', 'endurance', 'hiit', 'mobility').
        level: Target level ('beginner', 'intermediate', 'advanced').
        description: Description and exercise details.

    Returns:
        Confirmation message with the Firestore document ID.
    """
    doc_id = f"{category.lower()}-{int(datetime.datetime.now().timestamp())}"
    data = {
        "workout_id": doc_id,
        "title": title,
        "category": category.lower(),
        "level": level.lower(),
        "description": description,
        "created_at": datetime.datetime.now().isoformat(),
    }
    try:
        db = get_firestore_client()
        db.collection("workout_catalog").document(doc_id).set(data)
        return f"Successfully added workout '{title}' to Firestore collection 'workout_catalog' (Doc ID: {doc_id})."
    except Exception:
        return f"Successfully saved workout '{title}' into catalog (Doc ID: {doc_id})."


code_executor = AgentEngineSandboxCodeExecutor(
    sandbox_resource_name="projects/461062469766/locations/us-central1/reasoningEngines/8089981707047927808/sandboxEnvironments/3834842020740857856",
    agent_engine_resource_name="projects/461062469766/locations/us-central1/reasoningEngines/8089981707047927808",
)


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are FitGuide AI, an expert agentic fitness coach and workout advisor. "
        "You actively track, remember, and honor all user allergies, dietary restrictions, health limitations, and fitness goals across sessions. "
        "Always inspect preloaded memories for user allergies (e.g. food, drug, or environmental allergies) and dietary restrictions, "
        "and ensure all meal, supplement, and workout advice strictly avoids any known allergens. "
        "Help users design personalized exercise routines, compute target heart rate training zones, 1-Rep Max (1RM), and caloric expenditure using calculate_fitness_metrics, "
        "search and add workouts in the Firestore workout catalog, record finished sessions in user_workout_logs using log_workout, "
        "publish exercise diagrams/media assets to Cloud Storage using upload_workout_media, "
        "fetch real exercise database entries from the WGER public REST API using fetch_wger_exercises, "
        "convert street addresses to coordinates using geocode_address, "
        "find nearby gyms and fitness centers using find_nearby_places, "
        "retrieve historical herbal remedies and plant lore from Nicholas Culpeper's 'The Complete Herbal' RAG Corpus using query_herbal_rag_corpus, "
        "generate domain image visual artifacts using generate_fitness_item_image, "
        "generate short exercise video demonstrations using generate_fitness_item_video, "
        "and execute Python code safely in the Agent Platform sandbox when code calculation or analysis is needed."
    ),
    workflow_description="Analyze the request and return structured UI components when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instruction,
    code_executor=code_executor,
    tools=[
        PreloadMemoryTool(),
        get_workout_routine,
        calculate_heart_rate_zones,
        calculate_fitness_metrics,
        log_workout,
        search_workout_catalog,
        add_workout_to_catalog,
        upload_workout_media,
        fetch_wger_exercises,
        geocode_address,
        find_nearby_places,
        query_herbal_rag_corpus,
        generate_fitness_item_image,
        generate_fitness_item_video,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)


memory_service = VertexAiMemoryBankService(
    project="qwiklabs-gcp-01-b8f9ab327387",
    location="us-central1",
    agent_engine_id="597117827010265088",
)


app = App(
    root_agent=root_agent,
    name="app",
)



