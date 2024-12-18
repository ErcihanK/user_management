import pytest
from httpx import AsyncClient
from uuid import UUID

@pytest.mark.asyncio
async def test_profile_validation(async_client, verified_user, user_token):
    """Test profile field validation"""
    invalid_data = {
        "first_name": "A" * 101,  # Too long
        "email": "notanemail",    # Invalid email
        "github_profile_url": "notaurl"  # Invalid URL
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=invalid_data,
        headers=headers
    )
    assert response.status_code == 422
    
@pytest.mark.asyncio
async def test_profile_partial_update(async_client, verified_user, user_token):
    """Test that partial updates work correctly"""
    update_data = {
        "bio": "New bio text"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["bio"] == "New bio text"
    # Other fields should remain unchanged
    assert response.json()["email"] == verified_user.email

@pytest.mark.asyncio
async def test_profile_urls(async_client, verified_user, user_token):
    """Test updating profile URLs"""
    update_data = {
        "github_profile_url": "https://github.com/testuser",
        "linkedin_profile_url": "https://linkedin.com/in/testuser",
        "profile_picture_url": "https://example.com/pic.jpg"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["github_profile_url"] == update_data["github_profile_url"]
    assert response.json()["linkedin_profile_url"] == update_data["linkedin_profile_url"]
    assert response.json()["profile_picture_url"] == update_data["profile_picture_url"]

@pytest.mark.asyncio
async def test_professional_status_notification(async_client, verified_user, admin_token, email_service):
    """Test that notifications are sent when professional status is updated"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/professional-status",
        params={"status": True},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["is_professional"] is True
    # Verify email service was called
    assert email_service.send_user_email.called

@pytest.mark.asyncio
async def test_profile_update_email_notification(async_client, verified_user, user_token, email_service):
    """Test that email notifications are sent when profile is updated"""
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    # Verify email notification was sent
    assert email_service.send_user_email.called

@pytest.mark.asyncio
async def test_manager_update_other_profile(async_client, verified_user, manager_token):
    """Test that managers can update other users' profiles"""
    update_data = {
        "bio": "Updated by manager"
    }
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["bio"] == "Updated by manager"

@pytest.mark.asyncio
async def test_profile_invalid_urls_format(async_client, verified_user, user_token):
    """Test validation of invalid URL formats"""
    invalid_urls = {
        "github_profile_url": "not-a-url",
        "linkedin_profile_url": "also-not-a-url",
        "profile_picture_url": "still-not-a-url"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=invalid_urls,
        headers=headers
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_profile_empty_update(async_client, verified_user, user_token):
    """Test that empty updates are handled properly"""
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json={},
        headers=headers
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_professional_status_unauthorized_user(async_client, verified_user, user_token):
    """Test that regular users cannot update professional status"""
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/professional-status",
        params={"status": True},
        headers=headers
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_profile_fields_length_limits(async_client, verified_user, user_token):
    """Test field length validation"""
    too_long_data = {
        "first_name": "A" * 101,  # Exceeds 100 character limit
        "last_name": "B" * 101,   # Exceeds 100 character limit
        "bio": "C" * 501          # Exceeds 500 character limit
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=too_long_data,
        headers=headers
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_profile_update_notification_content(async_client, verified_user, user_token, email_service):
    """Test that email notifications contain correct field information"""
    update_data = {
        "first_name": "Updated",
        "last_name": "Name",
        "bio": "New bio"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    # Verify email content
    assert email_service.send_user_email.called
    call_args = email_service.send_user_email.call_args
    assert "first_name" in call_args[0][2]
    assert "last_name" in call_args[0][2]
    assert "bio" in call_args[0][2]
