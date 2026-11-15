import json
import uuid
from datetime import datetime, timezone
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def lambda_handler(event, context):
    service = event.get("service", "AWS Service")
    error_msg = event.get("error_message", "")
    region = event.get("region", "us-east-1")

    prompt = (
        f"You are an AWS Principal Site Reliability Engineer. Analyze this incident:\n"
        f"Service: {service}\nRegion: {region}\nError: {error_msg}\n\n"
        f"Respond ONLY in valid JSON with keys: "
        f"'severity' (P1/P2/P3), 'summary' (concise root cause analysis), "
        f"and 'remediation' (a single string with exact AWS CLI commands to diagnose or mitigate)."
    )

    body = json.dumps({
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {"maxTokens": 400, "temperature": 0.2}
    })

    response = bedrock.invoke_model(
        modelId="amazon.nova-lite-v1:0",
        body=body
    )
    result = json.loads(response["body"].read())
    ai_text = result["output"]["message"]["content"][0]["text"]
    clean_json = ai_text.replace("```json", "").replace("```", "").strip()
    parsed = json.loads(clean_json)

    remediation = parsed.get("remediation", "Check CloudWatch Logs")
    if isinstance(remediation, list):
        remediation = "\n".join(str(item) for item in remediation)
    elif not isinstance(remediation, str):
        remediation = json.dumps(remediation)

    summary = parsed.get("summary", ai_text)
    if not isinstance(summary, str):
        summary = json.dumps(summary)

    return {
        "incident_id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "severity": str(parsed.get("severity", "P2")),
        "summary": summary,
        "remediation": remediation
    }
