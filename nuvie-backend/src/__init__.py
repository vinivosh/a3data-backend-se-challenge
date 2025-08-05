from fastapi import FastAPI
from sqlmodel import Session

import constants as c
from logger import log

# from api import api_router
from db import engine, init_db


app = FastAPI(
    title=c.PROJECT_NAME,
)

log.debug("Initializing connection to DB...")
with Session(engine) as session:
    init_db(session)
    log.debug("Connected to DB with success.")


# app.include_router(api_router, prefix=c.API_V1_STR)


@app.get("/")
def read_root():
    return {"msg": "Olá, mundo! Bem-vindo ao Nuvie Backend!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
