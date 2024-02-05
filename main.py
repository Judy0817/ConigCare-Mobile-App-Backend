from fastapi import FastAPI

from api import process_word

app = FastAPI()



@app.post("/items/")
async def create_item(item: dict):
   name = item["word"]
   return process_word(name)
