cd ~/zero-ops-triage

cat << 'EOF' > README.md
# Zero-Ops Incident Triage with AWS Step Functions & Amazon Bedrock

Serverless, event-driven incident triage pipeline built with **AWS SAM**, **Amazon API Gateway (HTTP API)**, **AWS Lambda**, **AWS Step Functions**, **Amazon Bedrock (`amazon.nova-lite-v1:0`)**, **Amazon DynamoDB**, and **Amazon SNS**.

## Architecture Flow
1. **Ingestion:** `POST /incident` on Amazon API Gateway invokes `TriggerWorkflowFunction` (`GET /incident` acts as a health check).
2. **Orchestration:** AWS Step Functions starts an execution of `IncidentWorkflowStateMachine`.
3. **AI Root-Cause Analysis:** `AnalyzeIncidentFunction` queries **Amazon Bedrock (`amazon.nova-lite-v1:0`)** to classify severity (`P1`–`P3`), summarize root cause, and generate AWS CLI remediation commands.
4. **Persistence:** Step Functions writes the structured post-mortem directly to **Amazon DynamoDB** (`PAY_PER_REQUEST` with 7-day TTL) via SDK integration.
5. **Notification:** Step Functions publishes the formatted post-mortem to on-call engineers via **Amazon SNS**.

## Deployment
```bash
sam build
sam deploy \
  --stack-name zero-ops-triage \
  --parameter-overrides AlertEmail=your-email@example.com \
  --capabilities CAPABILITY_IAM \
  --resolve-s3 \
  --region us-east-1
