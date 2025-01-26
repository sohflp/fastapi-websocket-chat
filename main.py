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
        request=request, name="base.html"
    )


@app.post("/user", response_class=HTMLResponse)
async def user(request: Request, username: str = Form(...)):
    return jinja.TemplateResponse(
        request=request, name="chat.html", context={'username': username}
    )


@app.websocket("/ws/{client_id}")
async def chat(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)

    # Rendering Jinja template
    notification = TEMPLATES['notification'].render({
        'username': client_id,
        'action': 'joined'
    })

    # Event: User connected
    await manager.broadcast(f"<span id=\"active\">{manager.active_users()}</span>")
    await manager.broadcast(f"<div id=\"history\" hx-swap-oob=\"beforeend\">{notification}</div>")

    try:
        while True:
            data = await websocket.receive_json()

            # Rendering Jinja template
            personal_message = TEMPLATES['user'].render({
                'message': data['message'],
                'username': client_id,
                'time': datetime.today().strftime("%I:%M %p")
            })
            global_message = TEMPLATES['global'].render({
                'message': data['message'],
                'username': client_id,
                'time': datetime.today().strftime("%I:%M %p")
            })

            # Event: New message sent / received
            await manager.broadcast(f"<span id=\"active\">{manager.active_users()}</span>")
            await manager.send_personal_message(f"<div id=\"history\" hx-swap-oob=\"beforeend\">{personal_message}</div>", websocket)
            await manager.send_global_message(f"<div id=\"history\" hx-swap-oob=\"beforeend\">{global_message}</div>", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

        # Rendering Jinja template
        notification = TEMPLATES['notification'].render({
            'username': client_id,
            'action': 'left'
        })

        # Event: User disconnected
        await manager.broadcast(f"<span id=\"active\">{manager.active_users()}</span>")
        await manager.broadcast(f"<div id=\"history\" hx-swap-oob=\"beforeend\">{notification}</div>")
