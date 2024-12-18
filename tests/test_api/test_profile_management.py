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

@pytest.mark.asyncio
async def test_invalid_github_url_format(async_client, verified_user, user_token):
    """Test that GitHub URL must have correct format"""
    update_data = {
        "github_profile_url": "https://wrongsite.com/user"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 422
    assert "GitHub URL" in response.json()["detail"]

@pytest.mark.asyncio
async def test_linkedin_url_validation(async_client, verified_user, user_token):
    """Test LinkedIn URL format validation"""
    invalid_url = {
        "linkedin_profile_url": "https://wrongsite.com/in/user"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=invalid_url,
        headers=headers
    )
    assert response.status_code == 422
    assert "LinkedIn URL" in response.json()["detail"]

@pytest.mark.asyncio
async def test_profile_picture_extension(async_client, verified_user, user_token):
    """Test profile picture URL extension validation"""
    invalid_extension = {
        "profile_picture_url": "https://example.com/pic.txt"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=invalid_extension,
        headers=headers
    )
    assert response.status_code == 422
    assert "image extensions" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_multiple_url_updates(async_client, verified_user, user_token):
    """Test updating multiple URLs simultaneously"""
    update_data = {
        "github_profile_url": "https://github.com/newuser",
        "linkedin_profile_url": "https://linkedin.com/in/newuser",
        "profile_picture_url": "https://example.com/newpic.jpg"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    assert all(update_data[k] == response.json()[k] for k in update_data.keys())

@pytest.mark.asyncio
async def test_professional_status_toggle(async_client, verified_user, admin_token):
    """Test toggling professional status"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Set to true
    response = await async_client.put(
        f"/users/{verified_user.id}/professional-status",
        params={"status": True},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["is_professional"] is True

    # Set to false
    response = await async_client.put(
        f"/users/{verified_user.id}/professional-status",
        params={"status": False},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["is_professional"] is False

@pytest.mark.asyncio
async def test_manager_update_profile_fields(async_client, verified_user, manager_token):
    """Test manager's ability to update various profile fields"""
    update_data = {
        "first_name": "Manager",
        "last_name": "Updated",
        "bio": "Updated by manager",
        "profile_picture_url": "https://example.com/pic.jpg"
    }
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    assert all(update_data[k] == response.json()[k] for k in update_data.keys())

@pytest.mark.asyncio
async def test_professional_status_notification_content(async_client, verified_user, admin_token, email_service):
    """Test professional status update email content"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/professional-status",
        params={"status": True},
        headers=headers
    )
    assert response.status_code == 200
    assert email_service.send_user_email.called
    call_args = email_service.send_user_email.call_args
    assert "upgraded" in call_args[0][2].lower()

@pytest.mark.asyncio
async def test_profile_update_with_spaces(async_client, verified_user, user_token):
    """Test handling of whitespace in profile fields"""
    update_data = {
        "first_name": "  John  ",
        "last_name": "  Doe  ",
        "bio": "  Bio with spaces  "
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == update_data["first_name"].strip()
    assert response.json()["last_name"] == update_data["last_name"].strip()
    assert response.json()["bio"] == update_data["bio"].strip()

@pytest.mark.asyncio
async def test_profile_update_special_characters(async_client, verified_user, user_token):
    """Test handling of special characters in profile fields"""
    update_data = {
        "first_name": "João-María",
        "last_name": "O'Connor-Smith",
        "bio": "Bio with émojis 🎉 and spécial chars @#$%"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == update_data["first_name"]
    assert response.json()["last_name"] == update_data["last_name"]
    assert response.json()["bio"] == update_data["bio"]

@pytest.mark.asyncio
async def test_consecutive_profile_updates(async_client, verified_user, user_token):
    """Test multiple consecutive profile updates"""
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # First update
    first_update = {"bio": "First update"}
    response1 = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=first_update,
        headers=headers
    )
    assert response1.status_code == 200
    assert response1.json()["bio"] == "First update"

    # Second update
    second_update = {"bio": "Second update"}
    response2 = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=second_update,
        headers=headers
    )
    assert response2.status_code == 200
    assert response2.json()["bio"] == "Second update"

@pytest.mark.asyncio
async def test_profile_update_content_validation(async_client, verified_user, user_token):
    """Test validation of profile content"""
    invalid_content = {
        "bio": "<script>alert('xss')</script>",
        "first_name": "Admin;DROP TABLE users;",
        "profile_picture_url": "javascript:alert('xss')"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=invalid_content,
        headers=headers
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_profile_input_sanitization(async_client, verified_user, user_token):
    """Test that input fields are properly sanitized"""
    unsafe_data = {
        "first_name": "<script>alert('xss')</script>John",
        "last_name": "Smith'; DROP TABLE users;--",
        "bio": "<style>body{background:red}</style>Bio"
    }
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(
        f"/users/{verified_user.id}/profile",
        json=unsafe_data,
        headers=headers
    )
    assert response.status_code == 200
    # Check that HTML and SQL injection attempts were removed
    assert "<script>" not in response.json()["first_name"]
    assert "DROP TABLE" not in response.json()["last_name"]
    assert "<style>" not in response.json()["bio"]
