import json 
import logging

from fastapi import HTTPException, requests
from app.models.PokeRequest import PokemonRequest
from app.utils.database import execute_query_json
from app.utils.AQueue import AQueue
from app.utils.ABlob import ABlob


# configurar el logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def insert_pokemon_request( pokemon_request: PokemonRequest) -> dict:
    try:
        query = " exec pokequeue.create_poke_requests ?, ?"
        logger.info(pokemon_request.sample_size)
        params = ( pokemon_request.pokemon_type, pokemon_request.sample_size, )
        result = await execute_query_json( query , params, True )
        result_dict = json.loads(result)
        logger.info(result)
        
        await AQueue().insert_message_on_queue( result )

        return result_dict
    except Exception as e:
        logger.error( f"Error inserting report reques {e}" )
        raise HTTPException( status_code=500 , detail="Internal Server Error" )
    
async def update_pokemon_request( pokemon_request: PokemonRequest) -> dict:
    try:
        query = " exec pokequeue.update_poke_request ?, ?, ? "

        if not pokemon_request.url:
            pokemon_request.url = ""

        params = ( pokemon_request.id, pokemon_request.status, pokemon_request.url)
        result = await execute_query_json( query , params, True )
        result_dict = json.loads(result)
        logger.info(result)
        return result_dict
    except Exception as e:
        logger.error( f"Error updating report reques {e}" )
        raise HTTPException( status_code=500 , detail="Internal Server Error" )
    
async def select_pokemon_request( id: int ):
    try:
        query = "select * from pokequeue.requests where id = ?"
        params = (id,)
        logger.info(f"id: {id}")
        result = await execute_query_json( query , params )
        result_dict = json.loads(result)
        return result_dict
    except Exception as e:
        logger.error( f"Error selecting report request {e}" )
        raise HTTPException( status_code=500 , detail="Internal Server Error" )

async def get_all_request() -> dict:
    query = """
        select 
            r.id as ReportId
            , s.description as Status
            , r.type as PokemonType
            , r.url 
            , r.created 
            , r.updated
        from pokequeue.requests r 
        inner join pokequeue.statuses s 
        on r.id_status = s.id 
    """
    result = await execute_query_json( query  )
    result_dict = json.loads(result)
    blob = ABlob()
    for record in result_dict:
        id_report = record['ReportId']
        record['url'] = f"{record['url']}?{blob.generate_sas(id_report)}"
    return result_dict

async def delete_pokemon_request(report_id: int):
    try:

        result_dict = await select_pokemon_request(report_id)

        if not result_dict:
            raise HTTPException(status_code=404, detail="Report not found")

        try:
            blob = ABlob()
            blob.delete_blob(report_id)
            logger.info(f"Blob {report_id} deleted successfully")
        except Exception as blob_error:
            logger.error(f"Error deleting blob: {blob_error}")
            raise HTTPException(status_code=500, detail="Error deleting file from Blob Storage")

        query_delete = "DELETE FROM pokequeue.requests WHERE id = ?"
        await execute_query_json(query_delete, (report_id,), True)
        logger.info(f"Report {report_id} deleted from the database")

        return {"message": f"Report {report_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")




