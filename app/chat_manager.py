from typing import Dict, List
from fastapi import WebSocket

class ConnetcionManager:
    def __init__(self):
        
        self.active_rooms: Dict[int, List[WebSocket]] = {}

    async def connect(self, grupo_id: int, websocket: WebSocket):
        await websocket.accept()
        if grupo_id not in self.active_rooms:
            self.active_rooms[grupo_id] = []
        self.active_rooms[grupo_id].append(websocket)

    def disconnect(self, grupo_id: int, websocket: WebSocket):
        if grupo_id in self.active_rooms:
            if websocket in self.active_rooms[grupo_id]:
                self.active_rooms[grupo_id].remove(websocket)
            if not self.active_rooms[grupo_id]:
                del self.active_rooms[grupo_id]

    async def broadcast_to_group(self, grupo_id: int, message: dict):
        if grupo_id in self.active_rooms:
            for connection in self.active_rooms[grupo_id]:
                await connection.send_json(message)

manager = ConnetcionManager()