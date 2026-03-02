#!/usr/bin/env bash
#
# Start Web UI Server with Reasoning Enabled
#
# DEPRECATED: Configure reasoning in config.yaml and use 'llm-stack server start'
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config.yaml"

# Show deprecation notice
echo "⚠️  This script is deprecated."
echo "   Configure reasoning in config.yaml and use:"
echo "   llm-stack server start"
echo ""

# Enable reasoning in config temporarily
if [ -f "$CONFIG_FILE" ]; then
    # Backup config
    cp "$CONFIG_FILE" "$CONFIG_FILE.bak"
    
    # Update reasoning settings using Python
    python3 << EOF
import yaml

with open("$CONFIG_FILE", "r") as f:
    config = yaml.safe_load(f)

config["reasoning"]["format"] = "deepseek"
config["reasoning"]["budget"] = -1
config["reasoning"]["enable_thinking"] = True

with open("$CONFIG_FILE", "w") as f:
    yaml.dump(config, f)

print("✅ Reasoning enabled in config.yaml")
EOF
    
    # Start server
    "$SCRIPT_DIR/start-webui.sh" "$@"
    
    # Restore config
    mv "$CONFIG_FILE.bak" "$CONFIG_FILE"
    echo "✅ Config restored"
else
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi
