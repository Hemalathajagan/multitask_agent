import httpx
from typing import Optional, Dict, Any, List
import streamlit as st

API_BASE_URL = "https://multitask-agent.onrender.com"


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
        self.timeout = 60.0  # 60 seconds for Render cold starts

    def set_token(self, token: str):
        self.token = token

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def register(self, email: str, username: str, password: str) -> Dict[str, Any]:
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.post(
                        f"{self.base_url}/auth/register",
                        json={"email": email, "username": username, "password": password},
                        headers=self._get_headers(),
                    )
                    if response.status_code == 201:
                        return {"success": True, "data": response.json()}
                    return {"success": False, "error": _safe_json_error(response, "Registration failed")}
            except httpx.ReadTimeout:
                if attempt < 2:
                    continue
                return {"success": False, "error": "Server is starting up. Please try again in a moment."}

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
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
            except httpx.ReadTimeout:
                if attempt < 2:
                    continue
                return {"success": False, "error": "Server is starting up. Please try again in a moment."}

    async def logout(self) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/auth/logout",
                headers=self._get_headers(),
            )
            self.token = None
            return {"success": True}

    async def get_me(self) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/auth/me",
                headers=self._get_headers(),
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": "Not authenticated"}

    async def create_task(self, objective: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
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
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/tasks/",
                params={"limit": limit},
                headers=self._get_headers(),
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": "Failed to fetch tasks"}

    async def get_task(self, task_id: int) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=self._get_headers(),
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": _safe_json_error(response, "Failed to fetch task")}

    async def rename_task(self, task_id: int, objective: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(
                f"{self.base_url}/tasks/{task_id}",
                json={"objective": objective},
                headers=self._get_headers(),
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": _safe_json_error(response, "Failed to rename task")}

    async def rerun_task(self, task_id: int) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/tasks/{task_id}/rerun",
                headers=self._get_headers(),
                timeout=30.0,
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": _safe_json_error(response, "Failed to rerun task")}

    async def continue_task(self, task_id: int, objective: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/tasks/{task_id}/continue",
                json={"objective": objective},
                headers=self._get_headers(),
                timeout=30.0,
            )
            if response.status_code == 201:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": _safe_json_error(response, "Failed to continue task")}

    async def update_profile(self, username: str = None, email: str = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
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
        async with httpx.AsyncClient(timeout=self.timeout) as client:
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

    async def get_pending_interaction(self, task_id: int) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/interactions/task/{task_id}/pending",
                headers=self._get_headers(),
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": "Failed to check interactions"}

    async def respond_to_interaction(self, request_id: int, response_data: dict) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/interactions/{request_id}/respond",
                json=response_data,
                headers=self._get_headers(),
            )
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": "Failed to respond to interaction"}

    async def update_photo(self, profile_photo: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
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
    try:
        return asyncio.run(client.register(email, username, password))
    except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.TimeoutException):
        return {"success": False, "error": "Server is starting up. Please try again in a moment."}


def sync_login(email: str, password: str) -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    try:
        result = asyncio.run(client.login(email, password))
    except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.TimeoutException):
        return {"success": False, "error": "Server is starting up. Please try again in a moment."}
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


def sync_rename_task(task_id: int, objective: str) -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    if "token" in st.session_state:
        client.set_token(st.session_state.token)
    return asyncio.run(client.rename_task(task_id, objective))


def sync_rerun_task(task_id: int) -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    if "token" in st.session_state:
        client.set_token(st.session_state.token)
    return asyncio.run(client.rerun_task(task_id))


def sync_continue_task(task_id: int, objective: str) -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    if "token" in st.session_state:
        client.set_token(st.session_state.token)
    return asyncio.run(client.continue_task(task_id, objective))


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


def sync_get_pending_interaction(task_id: int) -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    if "token" in st.session_state:
        client.set_token(st.session_state.token)
    return asyncio.run(client.get_pending_interaction(task_id))


def sync_respond_to_interaction(request_id: int, response_data: dict) -> Dict[str, Any]:
    import asyncio
    client = get_api_client()
    if "token" in st.session_state:
        client.set_token(st.session_state.token)
    return asyncio.run(client.respond_to_interaction(request_id, response_data))
