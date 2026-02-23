#!/bin/bash
# Updates the PROPSTREAM_API_URL on Railway when the tunnel URL changes
# Called by start.sh after tunnel comes up

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RAILWAY_TOKEN="888f4272-3672-4967-9f1e-20ab26fbb03a"
PROJECT_ID="af8383d8-62ed-4c33-8aef-8006071e07a2"
SERVICE_ID="062da69f-00ce-4ad9-afae-90c02f0c5dc9"
ENV_ID="3351321c-bfe1-486e-a607-b951a70094f9"

TUNNEL_URL="$1"

if [ -z "$TUNNEL_URL" ]; then
    echo "Usage: $0 <tunnel-url>"
    exit 1
fi

API_URL="${TUNNEL_URL}/api/lookup"

echo "Updating PROPSTREAM_API_URL to: $API_URL"

RESULT=$(curl -s -X POST "https://backboard.railway.app/graphql/v2" \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"mutation { variableUpsert(input: { projectId: \\\"$PROJECT_ID\\\", serviceId: \\\"$SERVICE_ID\\\", environmentId: \\\"$ENV_ID\\\", name: \\\"PROPSTREAM_API_URL\\\", value: \\\"$API_URL\\\" }) }\"}")

if echo "$RESULT" | grep -q '"variableUpsert":true'; then
    echo "✅ PROPSTREAM_API_URL updated"

    # Also update LEAD_INTEL_WEBHOOK_URL (same tunnel, different endpoint)
    curl -s -X POST "https://backboard.railway.app/graphql/v2" \
      -H "Authorization: Bearer $RAILWAY_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"query\":\"mutation { variableUpsert(input: { projectId: \\\"$PROJECT_ID\\\", serviceId: \\\"$SERVICE_ID\\\", environmentId: \\\"$ENV_ID\\\", name: \\\"LEAD_INTEL_WEBHOOK_URL\\\", value: \\\"$TUNNEL_URL\\\" }) }\"}" >/dev/null
    echo "✅ LEAD_INTEL_WEBHOOK_URL updated"
    
    # Trigger redeploy
    curl -s -X POST "https://backboard.railway.app/graphql/v2" \
      -H "Authorization: Bearer $RAILWAY_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"query\":\"mutation { serviceInstanceRedeploy(serviceId: \\\"$SERVICE_ID\\\", environmentId: \\\"$ENV_ID\\\") }\"}" >/dev/null
    echo "✅ Dialer redeploying"
else
    echo "❌ Failed to update Railway: $RESULT"
fi
