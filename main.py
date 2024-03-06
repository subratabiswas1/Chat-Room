from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dataclasses import dataclass
from typing import Dict
import uuid
import json
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

templates = Jinja2Templates(directory="templates")

@dataclass
class ConnectionManager:
  def __init__(self) -> None:
    self.active_connections: dict = {}
    self.active_usernames: dict = {}

  async def connect(self, websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    username = json.loads(data)

    id = str(uuid.uuid4())
    self.active_connections[id] = websocket
    self.active_usernames[id] = username
    for connection in self.active_connections.values():
      is_me = False
      if connection == websocket:
        is_me = True
      await connection.send_text(json.dumps({"isMe": is_me, "data": " have joined!!", "username": username['username']}))

  async def send_message(self, websocket: WebSocket, message: str):
    await websocket.send_text(message)

  def find_connection_id(self, websocket: WebSocket):
    websocket_list = list(self.active_connections.values())
    id_list = list(self.active_connections.keys())

    pos = websocket_list.index(websocket)
    return id_list[pos]

  async def broadcast(self, webSocket: WebSocket, data: str):
    decoded_data = json.loads(data)

    for connection in self.active_connections.values():
      is_me = False
      if connection == webSocket:
        is_me = True

      await connection.send_text(json.dumps({"isMe": is_me, "data": decoded_data['message'], "username": decoded_data['username']}))

  def disconnect(self, websocket: WebSocket):
    id = self.find_connection_id(websocket)
    username = self.active_connections[id]
    # data = await websocket.receive_text()
    del self.active_connections[id]
    # if(data):
    #     for connection in self.active_connections.values():
    #         await connection.send_text(json.dumps({"isMe": False, "data": " has left the room", "username": username}))
    return id

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
connection_manager = ConnectionManager()

app.add_middleware(
  CORSMiddleware,
  allow_origins = ["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def get_room(request: Request):
  return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/message")
async def websocket_endpoint(websocket: WebSocket):
  # Accept the connection from the client.
  await connection_manager.connect(websocket)

  try:
    while True:
      # Recieves message from the client
      data = await websocket.receive_text()
      await connection_manager.broadcast(websocket, data)
  except WebSocketDisconnect:
    id = connection_manager.disconnect(websocket)

    return RedirectResponse("/")
