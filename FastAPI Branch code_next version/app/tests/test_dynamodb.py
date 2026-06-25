from app.services.dynamodb_service import DynamoDBService

db = DynamoDBService()

result = db.save_metadata(
    "sample.txt",
    24
)

print(result)