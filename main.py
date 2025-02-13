from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from chat.websocket import ConnectionManager

from datetime import datetime

jinja = Jinja2Templates(directory="templates")
manager = ConnectionManager()

TEMPLATES = {
    'notification': jinja.get_template(name="messages/notification.html"),
    'user': jinja.get_template(name="messages/user.html"),
    'global': jinja.get_template(name="messages/global.html"),
}

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return jinja.TemplateResponse(
        request=request,
        name="base.html"
    )


@app.post("/user", response_class=HTMLResponse)
async def user(request: Request, username: str = Form(...)):
    return jinja.TemplateResponse(
        request=request,
        name="chat.html",
        context={'username': username}
    )


@app.post("/message", response_class=HTMLResponse)
async def message(
    request: Request,
    username: str = Form(...),
    message: str = Form(...)
):
    # Send global message to other users via WS
    global_message = TEMPLATES['global'].render({
        'message': message,
        'username': username,
        'time': datetime.today().strftime("%I:%M %p")
    })
    await manager.send_global_message(username, f"<div id=\"history\" hx-swap-oob=\"beforeend\">{global_message}</div>")

    # Return personal message via AJAX
    return jinja.TemplateResponse(
        request=request,
        name="messages/user.html",
        context={
            'message': message,
            'username': username,
            'time': datetime.today().strftime("%I:%M %p")
        }
    )


@app.websocket("/ws/{username}")
async def chat(websocket: WebSocket, username: str):
    await manager.connect(username, websocket)

    # Rendering Jinja template
    notification = TEMPLATES['notification'].render({
        'username': username,
        'action': 'joined'
    })

    # Event: User connected
    await manager.send_broadcast(f"<span id=\"active\">{manager.active_users()}</span>")
    await manager.send_broadcast(f"<div id=\"history\" hx-swap-oob=\"beforeend\">{notification}</div>")

    try:
        while True:
            await websocket.receive_json()  # No action required due to new "/message" route

    except WebSocketDisconnect:
        manager.disconnect(username)

        # Rendering Jinja template
        notification = TEMPLATES['notification'].render({
            'username': username,
            'action': 'left'
        })

        # Event: User disconnected
        await manager.send_broadcast(f"<span id=\"active\">{manager.active_users()}</span>")
        await manager.send_broadcast(f"<div id=\"history\" hx-swap-oob=\"beforeend\">{notification}</div>")
