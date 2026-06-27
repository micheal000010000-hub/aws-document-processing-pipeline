import os
from dotenv import load_dotenv

load_dotenv()

AWS_ENDPOINT = os.getenv("AWS_ENDPOINT")
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")