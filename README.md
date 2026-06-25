# AWS Document Processing Pipeline

Learning AWS by building instead of only reading documentation.

This project demonstrates how core AWS services interact in a serverless workflow using **Floci**, an open-source AWS emulator.

## Technologies

* Python
* Docker
* Floci
* AWS CLI
* Amazon S3
* AWS Lambda
* DynamoDB
* IAM Concepts

---

## Architecture

```
Document
    │
    ▼
Amazon S3
    │
    ▼
AWS Lambda
    │
    ▼
Generate Metadata
    │
    ▼
Amazon DynamoDB
```

---

## What I Learned

* Creating and managing S3 buckets
* Uploading and downloading objects
* Creating DynamoDB tables
* Reading and writing DynamoDB items
* Building and deploying Lambda functions
* Invoking Lambda with event payloads
* Understanding IAM users, roles and policies
* Debugging Lambda runtime issues
* Understanding service-to-service communication

---

## Project Structure

```
document-processing-pipeline/

├── uploads/
│   └── sample.txt
│
├── lambda/
│   ├── handler.py
│   ├── event.json
│   └── function.zip
│
└── README.md
```

---

## Running Floci

```bash
docker compose up -d
```

---

## Configure AWS CLI

```bash
aws configure
```

Example credentials:

```
Access Key : test
Secret Key : test
Region     : us-east-1
Output     : json
```

---

## Create S3 Bucket

```bash
aws --endpoint-url=http://localhost:4566 \
s3 mb s3://document-bucket
```

---

## Create DynamoDB Table

```bash
aws --endpoint-url=http://localhost:4566 \
dynamodb create-table \
--table-name Documents \
--attribute-definitions AttributeName=documentId,AttributeType=S \
--key-schema AttributeName=documentId,KeyType=HASH \
--billing-mode PAY_PER_REQUEST
```

---

## Deploy Lambda

```bash
zip function.zip handler.py
```

```bash
aws --endpoint-url=http://localhost:4566 \
lambda create-function \
--function-name DocumentMetadataProcessor \
--runtime python3.11 \
--handler handler.lambda_handler \
--zip-file fileb://function.zip \
--role arn:aws:iam::000000000000:role/lambda-role
```

---

## Invoke Lambda

```bash
aws --endpoint-url=http://localhost:4566 \
lambda invoke \
--function-name DocumentMetadataProcessor \
--payload file://event.json \
--cli-binary-format raw-in-base64-out \
response.json
```

---

## Notes

Floci successfully emulates the core AWS services used in this project. During development I also explored Lambda-to-DynamoDB communication using `boto3`. The final automatic write was limited by Floci's local networking behavior, which provided a useful opportunity to learn about Lambda runtime isolation and debugging.

