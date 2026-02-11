from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import asyncio

router = APIRouter()

# Store active WebSocket connections by task_id
active_connections: Dict[int, Set[WebSocket]] = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: int):
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = set()
        self.active_connections[task_id].add(websocket)

    def disconnect(self, websocket: WebSocket, task_id: int):
        if task_id in self.active_connections:
            self.active_connections[task_id].discard(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

    async def broadcast_to_task(self, task_id: int, message: dict):
        if task_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[task_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            # Clean up disconnected sockets
            for conn in disconnected:
                self.active_connections[task_id].discard(conn)


manager = ConnectionManager()


@router.websocket("/ws/task/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: int):
    await manager.connect(websocket, task_id)
    try:
        while True:
            # Keep connection alive, wait for messages
            data = await websocket.receive_text()
            # Echo back for now (can be extended for bidirectional communication)
            await websocket.send_json({"type": "ack", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)


async def send_agent_message(task_id: int, agent_name: str, content: str):
    """Send agent message to all connected clients for a task."""
    await manager.broadcast_to_task(task_id, {
        "type": "agent_message",
        "agent_name": agent_name,
        "content": content
    })


async def send_status_update(task_id: int, status: str):
    """Send status update to all connected clients for a task."""
    await manager.broadcast_to_task(task_id, {
        "type": "status_update",
        "status": status
    })


async def send_input_request(task_id: int, request_id: int, tool_name: str, prompt: str, fields: list):
    """Send input request to all connected clients for a task."""
    await manager.broadcast_to_task(task_id, {
        "type": "request_input",
        "request_id": request_id,
        "tool_name": tool_name,
        "prompt": prompt,
        "fields": fields,
    })


async def send_confirmation_request(task_id: int, request_id: int, tool_name: str, description: str, parameters: dict):
    """Send confirmation request to all connected clients for a task."""
    await manager.broadcast_to_task(task_id, {
        "type": "request_confirmation",
        "request_id": request_id,
        "tool_name": tool_name,
        "description": description,
        "parameters": parameters,
    })
