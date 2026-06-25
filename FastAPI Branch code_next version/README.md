# Document Processing Pipeline (FastAPI + Floci)

## Overview

A cloud-native document processing backend built using **FastAPI** while learning AWS locally through **Floci**.

Instead of using a paid AWS account, the application communicates with Floci, which emulates AWS services such as Amazon S3, DynamoDB, and Lambda.

The goal of this project is to understand how backend applications interact with cloud services using the official AWS SDK (`boto3`) rather than the AWS CLI.

---

## Features

* Upload documents using FastAPI
* Store files in Amazon S3 (Floci)
* Modular storage service architecture
* DynamoDB metadata service
* Automatic creation of S3 buckets during application startup
* Swagger/OpenAPI documentation

---

## Project Structure

```
document-processing-pipeline/

├── app/
│   ├── main.py
│   ├── routes/
│   │   └── upload.py
│   ├── services/
│   │   ├── s3_storage.py
│   │   └── dynamodb_service.py
│   └── tests/
│       └── test_dynamodb.py
│
├── uploads/
├── requirements.txt
└── README.md
```

---

## Architecture

```
Client

    │

    ▼

FastAPI

    │

    ├──────────────► S3 Storage Service

    │                     │

    │                     ▼

    │                Amazon S3 (Floci)

    │

    └──────────────► DynamoDB Service

                          │

                          ▼

                    Amazon DynamoDB (Floci)
```

---

## Technologies

* Python
* FastAPI
* boto3
* Floci
* Docker
* AWS CLI

---

## Running the Project

### Start Floci

```bash
docker compose up -d
```

### Install dependencies

```bash
python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

### Start FastAPI

```bash
uvicorn app.main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

---

## Current Status

### Completed

* FastAPI project setup
* File upload endpoint
* S3 integration using boto3
* Automatic bucket creation
* DynamoDB service implementation
* Service layer architecture

### Work in Progress

* DynamoDB metadata integration debugging

### Planned

* List documents
* Download document
* Delete document
* Lambda integration
* Docker deployment
* GitHub Actions
* EC2 deployment

```
```
