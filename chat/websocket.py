from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket

    def active_users(self):
        return len(self.active_connections)

    def disconnect(self, username: str):
        self.active_connections.pop(username)

    async def send_global_message(self, username: str, message: str):
        for id, connection in self.active_connections.items():
            if id == username:
                continue
            await connection.send_text(message)

    async def send_broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)
