# User Management API Project

## Completed Issues and Solutions
1. [User Profile Management Implementation #1](https://github.com/ErcihanK/user_management/issues/1)
   Implemented comprehensive user profile management functionality including professional status updates, field validation, and email notifications. Added proper error handling and field sanitization to ensure secure profile updates.

2. [Profile Update Email Notifications #2](https://github.com/ErcihanK/user_management/issues/2)
   Enhanced the email notification system for profile updates with detailed change tracking and improved error handling. Implemented proper email templates and notification triggers for various profile changes.

3. [URL Validation Enhancement #3](https://github.com/ErcihanK/user_management/issues/3)
   Strengthened URL validation for profile fields by implementing strict format checking for GitHub, LinkedIn, and profile picture URLs. Added comprehensive validation rules and proper error messaging.

4. [Professional Status Management #4](https://github.com/ErcihanK/user_management/issues/4)
   Implemented role-based access control for professional status updates, allowing only admins and managers to modify user status. Added email notifications for status changes and proper validation.

5. [Profile Statistics Implementation #5](https://github.com/ErcihanK/user_management/issues/5)
   Added comprehensive profile statistics tracking including update counts, last modification timestamps, and professional status history. Implemented admin/manager-only access to statistics endpoints.
![image](https://github.com/user-attachments/assets/3b23ae95-3622-4907-8306-8e61d7737f19)

## Docker Image
The project is containerized and available on DockerHub:
- Repository: [ercihankorkmaz/user_management](https://hub.docker.com/repository/docker/ercihankorkmaz/user_management)
- Latest Image: `ercihankorkmaz/user_management:latest`

1. Test Profile Validation (Lines 6-23):
[Test Profile Validation](https://github.com/ErcihanK/user_management/blob/main/tests/test_api/test_profile_management.py#L6-L23)
Test Profile URLs (Lines 44-64):
Test Professional Status Notification (Lines 66-81):
Test Email Notification Content (Lines 83-99):
Test Manager Update Permissions (Lines 101-116):
Test Invalid URL Formats (Lines 118-134):
Test Professional Status Toggle (Lines 193-215):
Test Special Characters Handling (Lines 267-285):
Test Consecutive Updates (Lines 287-313):
Test User Statistics (Lines 315-337):
