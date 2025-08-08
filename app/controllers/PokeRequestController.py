import json 
import logging

from fastapi import HTTPException
from app.models.PokeRequest import PokemonRequest
from app.utils.database import execute_query_json
from app.utils.AQueue import AQueue


# configurar el logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def insert_pokemon_request( pokemon_request: PokemonRequest) -> dict:
    try:
        query = " exec pokequeue.create_poke_requests ? "
        params = ( pokemon_request.pokemon_type,  )
        result = await execute_query_json( query , params, True )
        result_dict = json.loads(result)
        logger.info(result)
        
        await AQueue().insert_message_on_queue( result )

        return result_dict
    except Exception as e:
        logger.error( f"Error inserting report reques {e}" )
        raise HTTPException( status_code=500 , detail="Internal Server Error" )


