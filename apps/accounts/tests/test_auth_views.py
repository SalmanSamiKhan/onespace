# gpt basic test cases
# """
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


# Registration
@pytest.mark.django_db
def test_user_registration(api_client):
    url = reverse("register")  # map this name in urls.py
    payload = {
        "name": "new user",
        "email": "newuser@example.com",
        "password": "testpass123",
        "password2": "testpass123",
    }
    response = api_client.post(url, data=payload)
    # print('response data: ', response.data)
    assert response.status_code == status.HTTP_201_CREATED
    assert "token" in response.data


# Login
@pytest.mark.django_db
def test_user_login(api_client, create_user):
    user = create_user()
    url = reverse("login")
    payload = {
        "email": user.email,
        "password": "strongpassword123",
    }
    response = api_client.post(url, data=payload)
    assert response.status_code == status.HTTP_200_OK
    assert "token" in response.data


# Profile (authenticated GET)
@pytest.mark.django_db
def test_user_profile(api_client, create_user):
    user = create_user()
    token = RefreshToken.for_user(user).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    url = reverse("profile")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "email" in response.data


# Change Password
@pytest.mark.django_db
def test_change_password(api_client, create_user):
    user = create_user()
    token = RefreshToken.for_user(user).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    url = reverse("change-password")
    payload = {
        "password": "newstrongpassword456",
        "password2": "newstrongpassword456",
    }
    response = api_client.post(url, data=payload)
    assert response.status_code == status.HTTP_200_OK


# """


# Gpt all test cases
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
def test_user_registration_success(api_client):
    url = reverse("register")
    payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "password123",
        "password2": "password123",
    }
    response = api_client.post(url, data=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert "token" in response.data


@pytest.mark.django_db
@pytest.mark.parametrize(
    "payload,expected_field",
    [
        (
            {
                "email": "testuser@example.com",
                "password": "password123",
                "password2": "diffpass",
                "name": "Test",
            },
            "password2",
        ),
        (
            {
                "email": "",
                "password": "password123",
                "password2": "password123",
                "name": "Test",
            },
            "email",
        ),
        (
            {
                "email": "testuser@example.com",
                "password": "",
                "password2": "",
                "name": "Test",
            },
            "password",
        ),
    ],
)
def test_user_registration_invalid_payload(api_client, payload, expected_field):
    url = reverse("register")
    response = api_client.post(url, data=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert expected_field in response.data


@pytest.mark.django_db
def test_user_login_success(api_client, create_user):
    user = create_user()
    url = reverse("login")
    payload = {"email": user.email, "password": "strongpassword123"}
    response = api_client.post(url, data=payload)
    assert response.status_code == status.HTTP_200_OK
    assert "token" in response.data


@pytest.mark.django_db
@pytest.mark.parametrize(
    "payload",
    [
        {"email": "wrong@example.com", "password": "strongpassword123"},
        {"email": "testuser@example.com", "password": "wrongpass"},
        {"email": "", "password": "password123"},
    ],
)
def test_user_login_failure(api_client, create_user, payload):
    create_user()  # create user to test against
    url = reverse("login")
    response = api_client.post(url, data=payload)
    assert (
        response.status_code == status.HTTP_400_BAD_REQUEST
        or response.status_code == status.HTTP_401_UNAUTHORIZED
        or response.status_code == status.HTTP_200_OK
        and "errors" in response.data
    )


@pytest.mark.django_db
def test_user_profile_success(api_client, create_user):
    user = create_user()
    token = RefreshToken.for_user(user).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    url = reverse("profile")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "email" in response.data


@pytest.mark.django_db
def test_user_profile_unauthenticated(api_client):
    url = reverse("profile")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_change_password_success(api_client, create_user):
    user = create_user()
    token = RefreshToken.for_user(user).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    url = reverse("change-password")
    payload = {"password": "newpassword123", "password2": "newpassword123"}
    response = api_client.post(url, data=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["msg"] == "Password changed successfully"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "payload,expected_field",
    [
        ({"password": "newpassword123", "password2": "diffpassword"}, "password2"),
        ({"password": "", "password2": ""}, "password"),
    ],
)
def test_change_password_invalid_payload(
    api_client, create_user, payload, expected_field
):
    user = create_user()
    token = RefreshToken.for_user(user).access_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    url = reverse("change-password")
    response = api_client.post(url, data=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert expected_field in response.data


@pytest.mark.django_db
def test_change_password_unauthenticated(api_client):
    url = reverse("change-password")
    payload = {"password": "newpassword123", "password2": "newpassword123"}
    response = api_client.post(url, data=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

"""

# Seek test cases

'''
import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestUserRegisterView:
    url = reverse('register')

    def test_register_success(self, client, user_data):
        response = client.post(self.url, data=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "msg" in response.data
        assert "token" in response.data
        assert response.data["msg"] == "Registration successful"

    def test_register_missing_email(self, client, user_data):
        data = user_data.copy()
        del data['email']
        response = client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_password_mismatch(self, client, user_data):
        data = user_data.copy()
        data['password2'] = 'differentpassword'
        response = client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert "Passwords do not match" in str(response.data['non_field_errors'])

    def test_register_weak_password(self, client, user_data):
        data = user_data.copy()
        data['password'] = '123'
        data['password2'] = '123'
        response = client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    def test_register_duplicate_email(self, client, user_data, active_user):
        response = client.post(self.url, data=user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data


@pytest.mark.django_db
class TestUserLoginView:
    url = reverse('login')

    def test_login_success(self, client, active_user, user_data):
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        response = client.post(self.url, data=login_data)
        assert response.status_code == status.HTTP_200_OK
        assert "msg" in response.data
        assert "token" in response.data
        assert response.data["msg"] == "Login successful"

    def test_login_invalid_password(self, client, active_user, user_data):
        login_data = {
            "email": user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post(self.url, data=login_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response.data
        assert response.data["errors"] == "Invlid username or password"

    def test_login_invalid_email(self, client, user_data):
        login_data = {
            "email": "nonexistent@example.com",
            "password": user_data["password"]
        }
        response = client.post(self.url, data=login_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response.data

    def test_login_inactive_user(self, client, inactive_user, user_data):
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        response = client.post(self.url, data=login_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response.data


@pytest.mark.django_db
class TestUserProfileView:
    url = reverse('profile')

    def test_get_profile_unauthenticated(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile_success(self, auth_client, active_user):
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == active_user.email
        assert response.data["name"] == active_user.name


@pytest.mark.django_db
class TestUserChangePasswordView:
    url = reverse('change-password')

    def test_change_password_unauthenticated(self, client):
        response = client.post(self.url, data={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_success(self, auth_client, active_user, user_data):
        data = {
            "old_password": user_data["password"],
            "new_password": "newtestpass123",
            "new_password2": "newtestpass123"
        }
        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["msg"] == "Password changed successfully"

    def test_change_password_wrong_old_password(self, auth_client):
        data = {
            "old_password": "wrongpassword",
            "new_password": "newtestpass123",
            "new_password2": "newtestpass123"
        }
        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in response.data

    def test_change_password_mismatch_new_passwords(self, auth_client, user_data):
        data = {
            "old_password": user_data["password"],
            "new_password": "newtestpass123",
            "new_password2": "differentpass123"
        }
        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert "Passwords do not match" in str(response.data['non_field_errors'])

    def test_change_password_weak_password(self, auth_client, user_data):
        data = {
            "old_password": user_data["password"],
            "new_password": "123",
            "new_password2": "123"
        }
        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data
'''