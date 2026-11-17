#!/bin/bash
# Installs automated video generation cron jobs:
# 1. Daily Short/Reel at 10:00 AM every day
# 2. Long-Form Episode at 2:00 PM every 4 days

WORKSPACE="/Users/rahulgupta/Desktop/Project/Kids animation"
PYTHON_BIN="$(which python3)"
NODE_BIN="$(dirname $(which node))"
LOG_DIR="$WORKSPACE/output"

mkdir -p "$LOG_DIR"

CRON_JOB_SHORT="0 10 * * * export PATH=\"$NODE_BIN:\$PATH\" && \"$PYTHON_BIN\" \"$WORKSPACE/scripts/auto_pipeline.py\" --mode short >> \"$LOG_DIR/cron_short.log\" 2>&1"
CRON_JOB_LONG="0 14 */4 * * export PATH=\"$NODE_BIN:\$PATH\" && \"$PYTHON_BIN\" \"$WORKSPACE/scripts/auto_pipeline.py\" --mode long >> \"$LOG_DIR/cron_long.log\" 2>&1"

if [ "$1" == "--uninstall" ]; then
    crontab -r 2>/dev/null
    echo "✅ Removed automated video cron jobs."
    exit 0
fi

# Append to crontab
(crontab -l 2>/dev/null; echo "$CRON_JOB_SHORT"; echo "$CRON_JOB_LONG") | crontab -

echo "============================================================"
echo "🎉 CRON JOBS INSTALLED SUCCESSFULLY!"
echo "============================================================"
echo "1. Daily Reel/Short: Every day at 10:00 AM"
echo "   $CRON_JOB_SHORT"
echo ""
echo "2. Long Episode: Every 4 days at 2:00 PM"
echo "   $CRON_JOB_LONG"
echo "============================================================"
echo "To view active crontab: crontab -l"
echo "To uninstall crontab: ./scripts/setup_cron.sh --uninstall"
echo "============================================================"
