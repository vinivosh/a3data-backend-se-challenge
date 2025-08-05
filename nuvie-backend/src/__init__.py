from fastapi import FastAPI

import nuvie_sdk as nuv

app = FastAPI()


@app.get("/")
def read_root():
    print("Nuvie Backend is running! Imported nuvie_sdk:", nuv)
    return {"msg": "Olá, mundo! Bem-vindo ao Nuvie Backend!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
