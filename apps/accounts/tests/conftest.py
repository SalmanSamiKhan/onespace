# gpt
# '''
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def make_user(**kwargs):
        defaults = {
            "name": "test user",
            "email": "testuser@example.com",
            "password": "strongpassword123",
        }
        defaults.update(kwargs)
        user = User.objects.create_user(**defaults)
        return user

    return make_user

# '''

# seek

'''
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user_data():
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpass123",
        "password2": "testpass123",
    }

@pytest.fixture
def inactive_user(user_data):
    user_data['is_active'] = False
    user = User.objects.create_user(
        email=user_data['email'],
        name=user_data['name'],
        password=user_data['password']
    )
    return user

@pytest.fixture
def active_user(user_data):
    user = User.objects.create_user(
        email=user_data['email'],
        name=user_data['name'],
        password=user_data['password']
    )
    user.is_active = True
    user.save()
    return user

@pytest.fixture
def auth_client(active_user, client):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(active_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client

'''