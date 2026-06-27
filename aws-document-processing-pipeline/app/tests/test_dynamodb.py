from app.services.dynamodb_service import DynamoDBService
from app.logger import logger
db = DynamoDBService()

result = db.save_metadata(
    "sample.txt",
    24
)

logger.info(f"Metadata saved: {result}")