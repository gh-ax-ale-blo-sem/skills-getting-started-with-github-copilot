"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
from pydantic import BaseModel, EmailStr, field_validator
from typing import List

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


class Activity(BaseModel):
    """Activity data model"""
    description: str
    schedule: str
    max_participants: int
    participants: List[str]
    
    @field_validator('max_participants')
    @classmethod
    def validate_max_participants(cls, v):
        if v <= 0:
            raise ValueError('max_participants must be positive')
        return v

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete against other schools",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 25,
        "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Improve swimming techniques and participate in swim meets",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["james@mergington.edu", "emily@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore various art mediums including painting, drawing, and sculpture",
        "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["lisa@mergington.edu", "ryan@mergington.edu"]
    },
    "Drama Club": {
        "description": "Participate in theater productions and improve acting skills",
        "schedule": "Thursdays, 3:30 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["natalie@mergington.edu", "david@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop critical thinking and public speaking through competitive debates",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["grace@mergington.edu", "ethan@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Compete in science and engineering challenges at regional competitions",
        "schedule": "Fridays, 3:00 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["lucy@mergington.edu", "william@mergington.edu"]
    }
}


def _get_activity(activity_name: str) -> dict:
    """Helper function to get activity and validate it exists"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activities[activity_name]


def _validate_email(email: str) -> str:
    """Validate email format"""
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Normalize email to lowercase
    email = email.lower().strip()
    
    # Basic email validation - could be enhanced with regex
    if not email.endswith("@mergington.edu"):
        raise HTTPException(status_code=400, detail="Only @mergington.edu emails are allowed")
    return email


@app.get("/")
def root():
    """Redirect root to static index page"""
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Get all available activities"""
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    activity = _get_activity(activity_name)
    email = _validate_email(email)

    # Check if activity is full
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    activity = _get_activity(activity_name)
    email = _validate_email(email)

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not registered for this activity")

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
