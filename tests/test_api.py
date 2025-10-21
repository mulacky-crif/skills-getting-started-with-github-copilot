"""
Test suite for the Mergington High School Activities API

This module contains comprehensive tests for all API endpoints including:
- GET /activities - Retrieve all activities
- POST /activities/{activity_name}/signup - Sign up for an activity
- DELETE /activities/{activity_name}/unregister - Unregister from an activity
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities data before each test."""
    # Save original state
    original_activities = {
        name: {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": details["participants"].copy()
        }
        for name, details in activities.items()
    }
    
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Test cases for GET /activities endpoint."""
    
    def test_get_activities_success(self, client):
        """Test successful retrieval of all activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check that each activity has required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_get_activities_contains_expected_activities(self, client):
        """Test that response contains expected default activities."""
        response = client.get("/activities")
        data = response.json()
        
        # Check for some expected activities
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        for activity in expected_activities:
            assert activity in data


class TestSignupForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify the participant was actually added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test that duplicate signup is rejected."""
        # First signup should succeed
        response1 = client.post(
            "/activities/Chess Club/signup?email=duplicate@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Chess Club/signup?email=duplicate@mergington.edu"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for a non-existent activity."""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_activity_full(self, client, reset_activities):
        """Test signup when activity is at maximum capacity."""
        # Fill up Chess Club (max 12 participants)
        chess_club = activities["Chess Club"]
        original_participants = chess_club["participants"].copy()
        
        # Add participants until it's full
        for i in range(chess_club["max_participants"] - len(original_participants)):
            chess_club["participants"].append(f"student{i}@mergington.edu")
        
        # Try to add one more participant
        response = client.post(
            "/activities/Chess Club/signup?email=overflow@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "full" in data["detail"].lower()
    
    def test_signup_missing_email(self, client):
        """Test signup without providing email parameter."""
        response = client.post("/activities/Chess Club/signup")
        
        assert response.status_code == 422  # Validation error


class TestUnregisterFromActivity:
    """Test cases for DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity."""
        # First sign up a participant
        signup_response = client.post(
            "/activities/Chess Club/signup?email=toberemoved@mergington.edu"
        )
        assert signup_response.status_code == 200
        
        # Then unregister them
        response = client.delete(
            "/activities/Chess Club/unregister?email=toberemoved@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "toberemoved@mergington.edu" in data["message"]
        
        # Verify the participant was actually removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "toberemoved@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistration from a non-existent activity."""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_not_signed_up(self, client):
        """Test unregistration when participant is not signed up."""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notsignedup@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant."""
        # Ensure Chess Club has at least one participant
        seed_email = "seeded@mergington.edu"
        signup_response = client.post(
            f"/activities/Chess Club/signup?email={seed_email}"
        )
        assert signup_response.status_code == 200

        # Get current participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        existing_participant = activities_data["Chess Club"]["participants"][0]
        
        # Unregister existing participant
        response = client.delete(
            f"/activities/Chess Club/unregister?email={existing_participant}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify removal
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        assert existing_participant not in updated_data["Chess Club"]["participants"]
    
    def test_unregister_missing_email(self, client):
        """Test unregistration without providing email parameter."""
        response = client.delete("/activities/Chess Club/unregister")
        
        assert response.status_code == 422  # Validation error


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static HTML."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple operations."""
    
    def test_complete_signup_unregister_flow(self, client, reset_activities):
        """Test complete flow: signup -> verify -> unregister -> verify."""
        email = "integration@mergington.edu"
        activity = "Programming Class"
        
        # Step 1: Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Step 2: Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Step 3: Verify signup
        after_signup_response = client.get("/activities")
        after_signup_data = after_signup_response.json()
        assert email in after_signup_data[activity]["participants"]
        assert len(after_signup_data[activity]["participants"]) == initial_count + 1
        
        # Step 4: Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Step 5: Verify unregistration
        final_response = client.get("/activities")
        final_data = final_response.json()
        assert email not in final_data[activity]["participants"]
        assert len(final_data[activity]["participants"]) == initial_count
    
    def test_multiple_participants_same_activity(self, client, reset_activities):
        """Test multiple participants signing up for the same activity."""
        activity = "Art Workshop"
        participants = [
            "artist1@mergington.edu",
            "artist2@mergington.edu", 
            "artist3@mergington.edu"
        ]
        
        # Sign up multiple participants
        for email in participants:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all are registered
        activities_response = client.get("/activities")
        activity_data = activities_response.json()[activity]
        
        for email in participants:
            assert email in activity_data["participants"]
    
    def test_participant_multiple_activities(self, client, reset_activities):
        """Test same participant signing up for multiple activities."""
        email = "multisport@mergington.edu"
        activities_to_join = ["Soccer Team", "Basketball Club", "Science Club"]
        
        # Sign up for multiple activities
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify participant is in all activities
        all_activities_response = client.get("/activities")
        all_activities_data = all_activities_response.json()
        
        for activity in activities_to_join:
            assert email in all_activities_data[activity]["participants"]