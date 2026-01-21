import httpx
from typing import Optional, Dict, Any, List
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"


def _safe_json_error(response: httpx.Response, default: str) -> str:
    """Safely extract error detail from response."""
    try:
        return response.json().get("detail", default)
    except Exception:
        return f"{default} (Status: {response.status_code})"


class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token: Optional[str] = None

    def set_token(self, token: str):
        self.token = token

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def register(self, email: str, username: str, password: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/register",
                json={"email": email, "username": username, "password": password},
                headers=self._get_headers(),
            )
            if response.status_code == 201:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": _safe_json_error(response, "Registration failed")}

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password},
                headers=self._get_headers(),
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                return {"success": True, "data": data}
            return {"success": False, "error": _safe_json_error(response, "Login failed")}

    async def logout(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/logout",
                headers=self._get_headers(),
            )
            self.token = None
            return {"success": True}

    async def get_me(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/auth/me",
                headers=self._get_headers(),
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": "Not authenticated"}

    async def create_task(self, objective: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/tasks/",
                json={"objective": objective},
                headers=self._get_headers(),
                timeout=30.0,
            )
            if response.status_code == 201:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": _safe_json_error(response, "Failed to create task")}

    async def get_tasks(self, limit: int = 50) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/tasks/",
                params={"limit": limit},
                headers=self._get_headers(),
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": "Failed to fetch tasks"}

    async def get_task(self, task_id: int) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=self._get_headers(),
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": _safe_json_error(response, "Failed to fetch task")}

    async def update_profile(self, username: str = None, email: str = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            data = {}
            if username:
                data["username"] = username
            if email:
                data["email"] = email

            response = await client.put(
                f"{self.base_url}/auth/profile",
                json=data,
                headers=self._get_headers(),
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": _safe_json_error(response, "Failed to update profile")}

    async def change_password(self, current_password: str, new_password: str, confirm_password: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/auth/password",
                json={
                    "current_password": current_password,
                    "new_password": new_password,
                    "confirm_password": confirm_password
                },
                headers=self._get_headers(),
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": _safe_json_error(response, "Failed to change password")}

    async def update_photo(self, profile_photo: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/auth/photo",
                json={"profile_photo": profile_photo},
                headers=self._get_headers(),
                timeout=60.0,
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": _safe_json_error(response, "Failed to update photo")}


# Synchronous wrappers for Streamlit
def get_api_client() -> APIClient:
    if "api_client" not in st.session_state:
        st.session_state.api_client = APIClient()
    return st.session_state.api_client


def sync_register(email: str, username: str, password: str) -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    return asyncio.run(client.register(email, username, password))


def sync_login(email: str, password: str) -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    result = asyncio.run(client.login(email, password))
    if result["success"]:
        st.session_state.token = client.token
    return result


def sync_logout() -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    result = asyncio.run(client.logout())
    if "token" in st.session_state:
        del st.session_state.token
    return result


def sync_get_me() -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    if "token" in st.session_state:
        client.set_token(st.session_state.token)
    return asyncio.run(client.get_me())


def sync_create_task(objective: str) -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    if "token" in st.session_state:
        client.set_token(st.session_state.token)
    return asyncio.run(client.create_task(objective))


def sync_get_tasks(limit: int = 50) -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    if "token" in st.session_state:
        client.set_token(st.session_state.token)
    return asyncio.run(client.get_tasks(limit))


def sync_get_task(task_id: int) -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    if "token" in st.session_state:
        client.set_token(st.session_state.token)
    return asyncio.run(client.get_task(task_id))


def sync_update_profile(username: str = None, email: str = None) -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    if "token" in st.session_state:
        client.set_token(st.session_state.token)
    return asyncio.run(client.update_profile(username, email))


def sync_change_password(current_password: str, new_password: str, confirm_password: str) -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    if "token" in st.session_state:
        client.set_token(st.session_state.token)
    return asyncio.run(client.change_password(current_password, new_password, confirm_password))


def sync_update_photo(profile_photo: str) -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    if "token" in st.session_state:
        client.set_token(st.session_state.token)
    return asyncio.run(client.update_photo(profile_photo))
