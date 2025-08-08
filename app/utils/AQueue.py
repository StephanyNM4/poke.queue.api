import os
import logging
from azure.storage.queue import QueueClient, BinaryBase64DecodePolicy, BinaryBase64EncodePolicy
from dotenv import load_dotenv

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AQueue:
    def __init__(self):
        try:
            self.azure_sak = os.getenv('AZURE_SAK')
            self.queue_name = os.getenv('QUEUE_NAME')

            if not self.azure_sak or not self.queue_name:
                raise ValueError("AZURE_SAK o QUEUE_NAME no están definidos en el entorno")

            self.queue_client = QueueClient.from_connection_string(
                self.azure_sak, self.queue_name
            )
            self.queue_client.message_decode_policy = BinaryBase64DecodePolicy()
            self.queue_client.message_encode_policy = BinaryBase64EncodePolicy()

            logger.info("QueueClient creado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar AQueue: {e}", exc_info=True)

    async def insert_message_on_queue(self, message: str):
        try:
            logger.info(f"Insertando mensaje en cola: {message}")
            message_bytes = message.encode('utf-8')

            # ¡OJO! send_message() es SINCRÓNICO, no uses 'await' aquí
            self.queue_client.send_message(
                self.queue_client.message_encode_policy.encode(message_bytes)
            )
            logger.info("Mensaje insertado correctamente")
        except Exception as e:
            logger.error(f"Error al insertar mensaje en la cola: {e}", exc_info=True)
