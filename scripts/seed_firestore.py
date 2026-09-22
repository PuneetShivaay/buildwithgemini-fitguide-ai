#!/usr/bin/env python3
"""Seed script for Firestore workout catalog database."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-b8f9ab327387"

SEED_WORKOUTS = [
    {
        "workout_id": "core-strength-01",
        "title": "Beginner Core & Lower Body Strength",
        "category": "strength",
        "level": "beginner",
        "target_muscle_groups": ["quads", "glutes", "abs", "lower_back"],
        "description": "Low-impact strength routine focused on core stability and knee safety.",
        "exercises": [
            {"name": "Goblet Squats", "sets": 3, "reps": "10-12"},
            {"name": "Dumbbell RDLs", "sets": 3, "reps": "12"},
            {"name": "Plank Hold", "sets": 3, "reps": "45 seconds"},
            {"name": "Bird-Dog Extensions", "sets": 3, "reps": "10 per side"},
        ],
    },
    {
        "workout_id": "zone2-endurance-01",
        "title": "Zone 2 Aerobic Engine Builder",
        "category": "endurance",
        "level": "intermediate",
        "target_muscle_groups": ["cardiovascular", "legs"],
        "description": "Steady-state aerobic base builder designed to stay within Zone 2 heart rate.",
        "exercises": [
            {"name": "Low-Impact Incline Walk or Cycling", "sets": 1, "reps": "45 minutes"},
            {"name": "Kettlebell Swings (Light)", "sets": 3, "reps": "15"},
            {"name": "Dead Hangs", "sets": 3, "reps": "30 seconds"},
        ],
    },
    {
        "workout_id": "upper-body-hiit-01",
        "title": "Upper Body & Core HIIT Burnout",
        "category": "hiit",
        "level": "advanced",
        "target_muscle_groups": ["chest", "shoulders", "triceps", "core"],
        "description": "High-intensity interval training focusing on upper body power and trunk stamina.",
        "exercises": [
            {"name": "Push-up to Side Plank", "sets": 4, "reps": "45 seconds on / 15 rest"},
            {"name": "Dumbbell Overhead Press", "sets": 4, "reps": "12"},
            {"name": "Mountain Climbers", "sets": 4, "reps": "45 seconds"},
            {"name": "Russian Twists", "sets": 4, "reps": "20"},
        ],
    },
]


def seed_firestore():
    print(f"Seeding Firestore collection 'workout_catalog' in project '{PROJECT_ID}'...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("workout_catalog")
    for workout in SEED_WORKOUTS:
        doc_ref = collection_ref.document(workout["workout_id"])
        doc_ref.set(workout)
        print(f"  ✓ Seeded document '{workout['workout_id']}': {workout['title']}")
    print("Firestore seeding complete!")


if __name__ == "__main__":
    seed_firestore()
