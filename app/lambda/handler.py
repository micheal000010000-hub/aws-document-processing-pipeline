import json
import logging


def lambda_handler(event, context):

    logging.info("=" * 60)

    logging.info("Lambda Invoked")

    logging.info("=" * 60)

    for record in event["Records"]:

        body = json.loads(record["body"])

        logging.info("Received Message:")

        logging.info(json.dumps(body, indent=4))

    return {
        "statusCode": 200
    }