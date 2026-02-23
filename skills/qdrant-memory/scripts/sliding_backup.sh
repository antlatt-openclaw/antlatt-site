#!/bin/bash
# sliding_backup.sh - Backup daily files to archive
# Run at 3:30 AM after Redis flush

set -e

WORKSPACE="/root/.openclaw/antlatt-workspace"
MEMORY_DIR="$WORKSPACE/memory"
ARCHIVE_DIR="$WORKSPACE/memory/archive"

# Create archive if needed
mkdir -p "$ARCHIVE_DIR"

# Get yesterday's date
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)

# Check if file exists
if [ -f "$MEMORY_DIR/$YESTERDAY.md" ]; then
    # Compress and move to archive
    gzip -c "$MEMORY_DIR/$YESTERDAY.md" > "$ARCHIVE_DIR/$YESTERDAY.md.gz"
    
    # Keep original for a week, then delete
    # (handled by separate cleanup cron)
    
    echo "✓ Archived $YESTERDAY.md"
else
    echo "No file to archive for $YESTERDAY"
fi

# Clean up archives older than 30 days
find "$ARCHIVE_DIR" -name "*.gz" -mtime +30 -delete 2>/dev/null || true

echo "✓ Backup complete"