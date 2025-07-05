#!/bin/bash

# Script to fix MiniMax TTS provider configuration
# Replaces the incorrect WebSocket implementation with the correct HTTP streaming approach

set -e

# Configuration
DB_CONTAINER="xiaozhi-esp32-server-db"
DB_USER="root"
DB_PASSWORD="123456"
DB_NAME="xiaozhi_esp32_server"
MYSQL_CHARSET="--default-character-set=utf8mb4"

echo "🔧 Fixing MiniMax TTS Provider Configuration"
echo "============================================="

# Function to execute MySQL command
execute_mysql() {
    local query="$1"
    local description="$2"
    echo "📝 $description"
    docker exec $DB_CONTAINER mysql -u $DB_USER -p$DB_PASSWORD $MYSQL_CHARSET $DB_NAME -e "$query"
    if [ $? -eq 0 ]; then
        echo "✅ Success: $description"
    else
        echo "❌ Failed: $description"
        exit 1
    fi
    echo ""
}

# Check container
if ! docker ps --format "table {{.Names}}" | grep -q "^$DB_CONTAINER$"; then
    echo "❌ Container '$DB_CONTAINER' is not running!"
    exit 1
fi

echo "🗑️  Removing incorrect WebSocket-based provider..."

# Remove old incorrect entries
execute_mysql "DELETE FROM ai_tts_voice WHERE tts_model_id = 'TTS_MinimaxDoubleStreamTTS';" \
    "Removing old voice entries"

execute_mysql "DELETE FROM ai_model_config WHERE id = 'TTS_MinimaxDoubleStreamTTS';" \
    "Removing old model config"

execute_mysql "DELETE FROM ai_model_provider WHERE id = 'SYSTEM_TTS_MinimaxDoubleStream';" \
    "Removing old provider entry"

echo "✨ Adding corrected MiniMax Enhanced Stream provider..."

# Add corrected provider
PROVIDER_SQL="INSERT INTO ai_model_provider (id, model_type, provider_code, name, fields, sort, creator, create_date, updater, update_date) VALUES (
'SYSTEM_TTS_MinimaxEnhancedStream', 
'TTS', 
'minimax_enhanced_stream', 
'MiniMax Enhanced Stream TTS', 
'[{\"key\":\"group_id\",\"label\":\"Group ID\",\"type\":\"string\"},{\"key\":\"api_key\",\"label\":\"API Key\",\"type\":\"string\"},{\"key\":\"model\",\"label\":\"Model\",\"type\":\"string\"},{\"key\":\"voice_id\",\"label\":\"Voice ID\",\"type\":\"string\"},{\"key\":\"host\",\"label\":\"API Host\",\"type\":\"string\"},{\"key\":\"voice_setting\",\"label\":\"Voice Settings\",\"type\":\"dict\",\"dict_name\":\"voice_setting\"},{\"key\":\"audio_setting\",\"label\":\"Audio Settings\",\"type\":\"dict\",\"dict_name\":\"audio_setting\"}]', 
17, 
1, 
NOW(), 
1, 
NOW()
);"

execute_mysql "$PROVIDER_SQL" "Adding corrected MiniMax Enhanced Stream Provider"

# Add corrected model config
MODEL_CONFIG_SQL="INSERT INTO ai_model_config VALUES (
'TTS_MinimaxEnhancedStreamTTS', 
'TTS', 
'MinimaxEnhancedStreamTTS', 
'MiniMax Enhanced Stream TTS', 
0, 
1, 
'{\"type\": \"minimax_enhanced_stream\", \"group_id\": \"your-minimax-group-id\", \"api_key\": \"your-minimax-api-key\", \"model\": \"speech-02-turbo\", \"voice_id\": \"female-shaonv\", \"host\": \"api.minimax.io\", \"voice_setting\": {\"speed\": 1, \"vol\": 1, \"pitch\": 0, \"emotion\": \"happy\"}, \"audio_setting\": {\"sample_rate\": 16000, \"bitrate\": 128000, \"format\": \"mp3\", \"channel\": 1}}', 
'https://www.minimax.io/platform/document/T2A%20V2', 
'MiniMax Enhanced Stream TTS Configuration:
1. Visit https://www.minimax.io/ to register for MiniMax account
2. Obtain Group ID and API Key from your MiniMax console
3. Uses standard HTTP API with enhanced parallel processing
4. Supports speech-02-turbo model for better performance
5. Processes text segments in parallel for lower latency
6. Compatible with ESP32 devices (16kHz audio output)
7. No WebSocket required - uses standard REST API', 
17, 
1, 
NOW(), 
1, 
NOW()
);"

execute_mysql "$MODEL_CONFIG_SQL" "Adding corrected model configuration"

# Add voice options
VOICES_SQL="INSERT INTO ai_tts_voice VALUES 
('TTS_MinimaxESS_0001', 'TTS_MinimaxEnhancedStreamTTS', 'Chinese Female Voice', 'female-shaonv', 'Chinese', 'https://static.minimax.io/audio/speech-02/female-shaonv.mp3', NULL, 1, 1, NOW(), 1, NOW()),
('TTS_MinimaxESS_0002', 'TTS_MinimaxEnhancedStreamTTS', 'Chinese Male Voice', 'male-qingnian', 'Chinese', 'https://static.minimax.io/audio/speech-02/male-qingnian.mp3', NULL, 2, 1, NOW(), 1, NOW()),
('TTS_MinimaxESS_0003', 'TTS_MinimaxEnhancedStreamTTS', 'English Female Voice', 'female-english', 'English', 'https://static.minimax.io/audio/speech-02/female-english.mp3', NULL, 3, 1, NOW(), 1, NOW()),
('TTS_MinimaxESS_0004', 'TTS_MinimaxEnhancedStreamTTS', 'English Male Voice', 'male-english', 'English', 'https://static.minimax.io/audio/speech-02/male-english.mp3', NULL, 4, 1, NOW(), 1, NOW());"

execute_mysql "$VOICES_SQL" "Adding voice options"

# Update Liquibase tracking
LIQUIBASE_SQL="INSERT INTO DATABASECHANGELOG (
ID, 
AUTHOR, 
FILENAME, 
DATEEXECUTED, 
ORDEREXECUTED, 
EXECTYPE, 
MD5SUM, 
DESCRIPTION, 
COMMENTS, 
TAG, 
LIQUIBASE, 
CONTEXTS, 
LABELS, 
DEPLOYMENT_ID
) VALUES (
'202507021600-fix', 
'fix-script', 
'fix-minimax-provider.sh', 
NOW(), 
(SELECT COALESCE(MAX(ORDEREXECUTED), 0) + 1 FROM DATABASECHANGELOG d), 
'EXECUTED', 
'8:fix_minimax', 
'Fix MiniMax TTS Provider Implementation', 
'Replace incorrect WebSocket with correct HTTP API', 
NULL, 
'4.20.0', 
NULL, 
NULL, 
CONCAT('fix_', UNIX_TIMESTAMP())
);"

execute_mysql "$LIQUIBASE_SQL" "Updating Liquibase changelog tracking"

echo "🔍 Verifying corrected installation..."

VERIFY_PROVIDER="SELECT id, name, provider_code FROM ai_model_provider WHERE provider_code = 'minimax_enhanced_stream';"
echo "📋 Checking corrected provider:"
docker exec $DB_CONTAINER mysql -u $DB_USER -p$DB_PASSWORD $MYSQL_CHARSET $DB_NAME -e "$VERIFY_PROVIDER"

VERIFY_VOICES="SELECT COUNT(*) as voice_count FROM ai_tts_voice WHERE tts_model_id = 'TTS_MinimaxEnhancedStreamTTS';"
echo "🎤 Checking voice count:"
docker exec $DB_CONTAINER mysql -u $DB_USER -p$DB_PASSWORD $MYSQL_CHARSET $DB_NAME -e "$VERIFY_VOICES"

echo ""
echo "✅ MiniMax TTS Provider Fix Complete!"
echo "====================================="
echo ""
echo "📋 Changes Made:"
echo "• Removed incorrect WebSocket-based provider"
echo "• Added corrected HTTP API-based provider"
echo "• Updated to use standard MiniMax REST API"
echo "• Maintained parallel processing for low latency"
echo ""
echo "📋 Next Steps:"
echo "1. Restart the web container:"
echo "   docker restart xiaozhi-esp32-server-web"
echo ""
echo "2. The corrected provider will be available as:"
echo "   'MiniMax Enhanced Stream TTS'"
echo ""
echo "3. Configure your MiniMax credentials in the web interface"
echo ""