# FastAPI WebSockets: Chat application

This app demonstrates the power of FastAPI and WebSockets to manage simultaneous two-way communication channel over a single TCP connection.

The following programming languages, technologies and frameworks were implemented as part of this project:

- [Python](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
    - [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
    - [FastAPI Templates](https://fastapi.tiangolo.com/advanced/templates/)
- [Jinja](https://jinja.palletsprojects.com/en/stable/)
- [tailwindcss](https://tailwindcss.com/)
- [htmx](https://htmx.org/)
    - [htmx Web Socket extension](https://htmx.org/extensions/ws/)

## Running

```shell
python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

fastapi run main.py

# Exit virtual environment (venv)
deactivate
```

Server started at http://0.0.0.0:8000
Documentation at http://0.0.0.0:8000/docs
