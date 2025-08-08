import uvicorn
import json
from fastapi import FastAPI
from app.utils.database import execute_query_json

from app.controllers.PokeRequestController import insert_pokemon_request

from app.models.PokeRequest import PokemonRequest

app = FastAPI()

@app.get("/")
async def root():
    query = "select * from pokequeue.MESSAGES"
    result = await execute_query_json(query)
    result_dict = json.loads(result)
    return result_dict

@app.get("/api/version")
async def root():
    return {"version": "0.1.0"}

@app.post("/api/request")
async def create_request(pokemon_request: PokemonRequest):
    return await insert_pokemon_request( pokemon_request )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)