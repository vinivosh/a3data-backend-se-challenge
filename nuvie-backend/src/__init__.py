from fastapi import FastAPI

import nuvie_sdk as nuv  # pyright: ignore[reportMissingImports]


app = FastAPI()


@app.get("/")
def read_root():
    return {"msg": "Olá, mundo! Bem-vindo ao Nuvie Backend!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
