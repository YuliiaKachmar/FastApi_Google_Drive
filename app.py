import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

import routes
from config import CLIENT_SECRET

app = FastAPI()
app.include_router(routes.router)
app.add_middleware(SessionMiddleware, secret_key=CLIENT_SECRET)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app="app:app", host="localhost", port=8000, reload=True)
