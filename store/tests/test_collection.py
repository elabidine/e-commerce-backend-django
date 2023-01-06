from rest_framework.test import APIClient
from rest_framework import status
import pytest

@pytest.mark.django_db
class TestCreateCollection:
   @pytest.mark.skip
   def if_use_anonymous_return_401(self):
        client = APIClient()
        response = client.post('/store/collection/',{'title':'a'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
