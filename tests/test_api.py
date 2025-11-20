"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the API"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
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
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root URL redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_success(self, client):
        """Test successfully retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_activities_structure(self, client):
        """Test that activity data has correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successfully signing up for an activity"""
        response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_already_registered(self, client):
        """Test signing up when already registered"""
        # Sign up first time
        client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        
        # Try to sign up again
        response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_activity_not_found(self, client):
        """Test signing up for non-existent activity"""
        response = client.post("/activities/Nonexistent Club/signup?email=test@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_with_special_characters(self, client):
        """Test signing up for activity with special characters in name"""
        response = client.post("/activities/Art%20Studio/signup?email=artist@mergington.edu")
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "artist@mergington.edu" in activities_data["Art Studio"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successfully unregistering from an activity"""
        # First, sign up
        client.post("/activities/Chess Club/signup?email=temporary@mergington.edu")
        
        # Then unregister
        response = client.delete("/activities/Chess Club/unregister?email=temporary@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert "temporary@mergington.edu" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "temporary@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_not_registered(self, client):
        """Test unregistering when not registered"""
        response = client.delete("/activities/Chess Club/unregister?email=notregistered@mergington.edu")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_activity_not_found(self, client):
        """Test unregistering from non-existent activity"""
        response = client.delete("/activities/Nonexistent Club/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        # michael@mergington.edu is already in Chess Club
        response = client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]


class TestIntegrationScenarios:
    """Integration tests for complete user scenarios"""
    
    def test_signup_and_unregister_flow(self, client):
        """Test complete flow of signing up and then unregistering"""
        email = "testflow@mergington.edu"
        activity = "Programming Class"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities")
        assert len(after_signup.json()[activity]["participants"]) == initial_count + 1
        assert email in after_signup.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        after_unregister = client.get("/activities")
        assert len(after_unregister.json()[activity]["participants"]) == initial_count
        assert email not in after_unregister.json()[activity]["participants"]
    
    def test_multiple_activities_signup(self, client):
        """Test signing up for multiple activities"""
        email = "multitask@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Art Studio"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all signups
        all_activities = client.get("/activities").json()
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]
