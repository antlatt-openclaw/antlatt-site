#!/bin/bash
# Uptime tracking script for antlatt.com
# Run via cron every 5 minutes: */5 * * * * /root/.openclaw/antlatt-workspace/website-redesign/antlatt-site/scripts/uptime-tracker.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_FILE="$PROJECT_DIR/public/api/uptime-data.json"
HISTORY_FILE="$PROJECT_DIR/public/api/uptime-history.json"

# Service endpoints (using local network)
SERVICES=(
  "Qdrant:http://192.168.1.202:6333/collections"
  "Redis:http://192.168.1.206:6379"
  "Ollama:http://192.168.1.207:11434/api/tags"
  "Website:http://localhost:8080/"
)

# Create output directory
mkdir -p "$PROJECT_DIR/public/api"

# Current timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Check a single service
check_service() {
  local name="$1"
  local url="$2"
  local start=$(date +%s%3N)
  local status="offline"
  local response_time=0
  
  # Use curl with timeout
  if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$url" 2>/dev/null | grep -q "200\|401\|403"; then
    status="online"
    local end=$(date +%s%3N)
    response_time=$((end - start))
  fi
  
  echo "{\"name\":\"$name\",\"status\":\"$status\",\"responseTime\":$response_time,\"timestamp\":\"$TIMESTAMP\"}"
}

# Check all services
RESULTS="["
FIRST=true
for service in "${SERVICES[@]}"; do
  name="${service%%:*}"
  url="${service#*:}"
  result=$(check_service "$name" "$url")
  
  if [ "$FIRST" = true ]; then
    FIRST=false
  else
    RESULTS+=","
  fi
  RESULTS+="$result"
done
RESULTS+="]"

# Calculate stats
ONLINE_COUNT=$(echo "$RESULTS" | grep -o '"status":"online"' | wc -l)
TOTAL_COUNT=${#SERVICES[@]}
# Use awk for floating point math (bc not installed)
UPTIME_PERCENT=$(awk "BEGIN {printf \"%.1f\", $ONLINE_COUNT * 100 / $TOTAL_COUNT}")

# Write current status
cat > "$DATA_FILE" << EOF
{
  "timestamp": "$TIMESTAMP",
  "services": $RESULTS,
  "stats": {
    "online": $ONLINE_COUNT,
    "total": $TOTAL_COUNT,
    "uptimePercent": $UPTIME_PERCENT
  }
}
EOF

# Update history (keep last 30 days of checks, one per hour)
if [ -f "$HISTORY_FILE" ]; then
  # Read existing history and add new entry
  jq --argjson new "{\"timestamp\":\"$TIMESTAMP\",\"uptime\":$UPTIME_PERCENT}" '. += [$new] | .[-720:]' "$HISTORY_FILE" > "$HISTORY_FILE.tmp" && mv "$HISTORY_FILE.tmp" "$HISTORY_FILE"
else
  # Create new history file
  echo "[{\"timestamp\":\"$TIMESTAMP\",\"uptime\":$UPTIME_PERCENT}]" > "$HISTORY_FILE"
fi

echo "Uptime check completed: $ONLINE_COUNT/$TOTAL_COUNT services online ($UPTIME_PERCENT%)"
