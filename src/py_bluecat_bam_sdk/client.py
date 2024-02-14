from httpx import Client, Response
from typing import Any, Self
import json


class Session:
    def __init__(self, token: str):
        self._token = token

    def get_token(self):
        return self._token

    def is_valid(self):
        pass


class APIClient:
    def __init__(self, base_url: str, client: Client | None = None):
        self._base_url = base_url
        if not client:
            self._client = Client(base_url=self._base_url)
        else:
            self._client = client
            self._client.headers.update({"Content-Type": "application/hal+json"})
        self._data = []

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    def login(self, username: str, password: str) -> Self:
        headers = {"Content-Type": "application/hal+json"}
        login_data = {"username": username, "password": password}
        login_result = self.post(
            path="api/v2/sessions",
            json=login_data,
            headers=headers
        )
        self._session = login_result.json()
        self._client.headers.update({"Authorization": f"Basic {self._session.get("basicAuthenticationCredentials")}"})
        return self

    def get(self, path, **kwargs) -> Response:
        return self._client.get(path, **kwargs)

    def post(self, path, **kwargs) -> Response:
        return self._client.post(path, **kwargs)

    @property
    def networks(self):
        api = NetworksAPI(base_url=self._base_url, client=self._client, resource_path="api/v2/networks")
        return api

    @property
    def configurations(self):
        api = ConfigurationsAPI(base_url=self._base_url, client=self._client)
        return api


class ConfigurationsAPI(APIClient):
    def __init__(self, base_url: str, client: Client | None = None, resource_path: str | None = None):
        super().__init__(base_url, client)
        self._resource_path = resource_path or "api/v2/configurations"
        self._data = []

    def get_by_name(self, name: str):
        query_params = f"?filter=name:contains('{name}')"
        api_data = self.get(self._resource_path + query_params).json().get("data")
        self._data = api_data
        return self

    def to_json(self):
        return json.dumps(self._data)


class NetworksAPI(APIClient):
    def __init__(self, base_url: str, client: Client | None = None, resource_path: str | None = None):
        super().__init__(base_url, client)
        self._resource_path = resource_path or "api/v2/networks"
        self._data = []

    def get_by_name(self, name: str):
        query_params = f"?filter=name:eq('{name}')"
        api_data = self.get(self._resource_path + query_params).json().get("data")
        self._data = api_data
        return self

    def to_json(self):
        return json.dumps(self._data)
