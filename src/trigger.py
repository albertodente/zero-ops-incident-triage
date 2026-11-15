import json
import os
import boto3

sfn = boto3.client("stepfunctions")
STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]

def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "POST")
    if method == "GET":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "service": "Zero-Ops Incident Triage API",
                "status": "ONLINE",
                "usage": "Send a POST request with JSON payload: {'service': '...', 'region': 'us-east-1', 'error_message': '...'}"
            })
        }

    body = json.loads(event.get("body") or "{}")
    payload = {
        "service": body.get("service", "unknown-service"),
        "error_message": body.get("error_message", "No details provided"),
        "region": body.get("region", "us-east-1")
    }
    resp = sfn.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        input=json.dumps(payload)
    )
    return {
        "statusCode": 202,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "status": "Workflow started",
            "executionArn": resp["executionArn"]
        })
    }
