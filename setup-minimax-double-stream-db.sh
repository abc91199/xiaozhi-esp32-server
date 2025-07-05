#!/bin/bash

# Script to inject MiniMax Double Stream TTS configuration into XiaoZhi ESP32 Server database
# This script handles a fresh database container setup

set -e  # Exit on any error

# Configuration
DB_CONTAINER="xiaozhi-esp32-server-db"
DB_USER="root"
DB_PASSWORD="123456"
DB_NAME="xiaozhi_esp32_server"
MYSQL_CHARSET="--default-character-set=utf8mb4"

echo "🚀 Setting up MiniMax Double Stream TTS in XiaoZhi ESP32 Server Database"
echo "=================================================="

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

# Function to wait for database to be ready
wait_for_database() {
    echo "⏳ Waiting for database to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec $DB_CONTAINER mysqladmin ping -h localhost -u $DB_USER -p$DB_PASSWORD >/dev/null 2>&1; then
            echo "✅ Database is ready!"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts - Database not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ Database failed to become ready after $max_attempts attempts"
    exit 1
}

# Function to check if container exists and is running
check_container() {
    if ! docker ps --format "table {{.Names}}" | grep -q "^$DB_CONTAINER$"; then
        echo "❌ Container '$DB_CONTAINER' is not running!"
        echo "   Please start your docker-compose setup first:"
        echo "   docker compose -f docker-compose-local.yml up -d"
        exit 1
    fi
    echo "✅ Container '$DB_CONTAINER' is running"
}

# Main execution
echo "🔍 Checking container status..."
check_container

echo ""
wait_for_database

echo ""
echo "🗃️  Injecting MiniMax Double Stream TTS Configuration..."

# 1. Clean up any existing entries
execute_mysql "DELETE FROM ai_model_provider WHERE id = 'SYSTEM_TTS_MinimaxDoubleStream';" \
    "Cleaning up existing provider entries"

execute_mysql "DELETE FROM ai_model_config WHERE id = 'TTS_MinimaxDoubleStreamTTS';" \
    "Cleaning up existing model config"

execute_mysql "DELETE FROM ai_tts_voice WHERE tts_model_id = 'TTS_MinimaxDoubleStreamTTS';" \
    "Cleaning up existing voice entries"

# 2. Insert AI Model Provider
PROVIDER_SQL="INSERT INTO ai_model_provider (id, model_type, provider_code, name, fields, sort, creator, create_date, updater, update_date) VALUES (
'SYSTEM_TTS_MinimaxDoubleStream', 
'TTS', 
'minimax_double_stream', 
'MiniMax Double Stream TTS', 
'[{\"key\":\"group_id\",\"label\":\"Group ID\",\"type\":\"string\"},{\"key\":\"api_key\",\"label\":\"API Key\",\"type\":\"string\"},{\"key\":\"model\",\"label\":\"Model\",\"type\":\"string\"},{\"key\":\"voice_id\",\"label\":\"Default Voice\",\"type\":\"string\"},{\"key\":\"host\",\"label\":\"API Host\",\"type\":\"string\"},{\"key\":\"voice_setting\",\"label\":\"Voice Settings\",\"type\":\"dict\",\"dict_name\":\"voice_setting\"},{\"key\":\"audio_setting\",\"label\":\"Audio Settings\",\"type\":\"dict\",\"dict_name\":\"audio_setting\"}]', 
17, 
1, 
NOW(), 
1, 
NOW()
);"

execute_mysql "$PROVIDER_SQL" "Adding MiniMax Double Stream TTS Provider"

# 3. Insert AI Model Config
MODEL_CONFIG_SQL="INSERT INTO ai_model_config VALUES (
'TTS_MinimaxDoubleStreamTTS', 
'TTS', 
'MinimaxDoubleStreamTTS', 
'MiniMax Double Stream TTS', 
0, 
1, 
'{\"type\": \"minimax_double_stream\", \"group_id\": \"your-minimax-group-id\", \"api_key\": \"your-minimax-api-key\", \"model\": \"speech-02-turbo\", \"voice_id\": \"female-shaonv\", \"host\": \"api.minimax.io\", \"voice_setting\": {\"speed\": 1, \"vol\": 1, \"pitch\": 0, \"emotion\": \"happy\"}, \"audio_setting\": {\"sample_rate\": 16000, \"bitrate\": 128000, \"format\": \"wav\", \"channel\": 1}}', 
NULL, 
NULL, 
17, 
NULL, 
NULL, 
NULL, 
NULL
);"

execute_mysql "$MODEL_CONFIG_SQL" "Adding MiniMax Double Stream TTS Model Configuration"

# 4. Update documentation
DOC_UPDATE_SQL="UPDATE ai_model_config SET 
doc_link = 'https://www.minimax.io/platform/document/T2A%20V2', 
remark = 'MiniMax Speech-02 Double Stream TTS Configuration:
1. Visit https://www.minimax.io/ to register for MiniMax account
2. Obtain Group ID and API Key from your MiniMax console
3. Recommended to use speech-02-turbo model for better real-time performance
4. Supports 30+ languages and 300+ voices
5. Sub-second latency with dual-stream processing capability
6. Configure sample_rate to 16000Hz for ESP32 device compatibility
7. Fill in your credentials in the configuration'
WHERE id = 'TTS_MinimaxDoubleStreamTTS';"

execute_mysql "$DOC_UPDATE_SQL" "Updating documentation and remarks"

# 5. Insert Voice Options
echo "🎤 Adding voice options..."

VOICES_SQL="INSERT INTO ai_tts_voice VALUES 
('TTS_MinimaxDoubleStreamTTS_0001', 'TTS_MinimaxDoubleStreamTTS', 'Chinese Female Voice', 'female-shaonv', 'Chinese', 'https://static.minimax.io/audio/speech-02/female-shaonv.mp3', NULL, 1, NULL, NULL, NULL, NULL),
('TTS_MinimaxDoubleStreamTTS_0002', 'TTS_MinimaxDoubleStreamTTS', 'Chinese Male Voice', 'male-qingnian', 'Chinese', 'https://static.minimax.io/audio/speech-02/male-qingnian.mp3', NULL, 2, NULL, NULL, NULL, NULL),
('TTS_MinimaxDoubleStreamTTS_0003', 'TTS_MinimaxDoubleStreamTTS', 'English Female Voice', 'female-english', 'English', 'https://static.minimax.io/audio/speech-02/female-english.mp3', NULL, 3, NULL, NULL, NULL, NULL),
('TTS_MinimaxDoubleStreamTTS_0004', 'TTS_MinimaxDoubleStreamTTS', 'English Male Voice', 'male-english', 'English', 'https://static.minimax.io/audio/speech-02/male-english.mp3', NULL, 4, NULL, NULL, NULL, NULL),
('TTS_MinimaxDoubleStreamTTS_0005', 'TTS_MinimaxDoubleStreamTTS', 'Japanese Female Voice', 'female-japanese', 'Japanese', 'https://static.minimax.io/audio/speech-02/female-japanese.mp3', NULL, 5, NULL, NULL, NULL, NULL),
('TTS_MinimaxDoubleStreamTTS_0006', 'TTS_MinimaxDoubleStreamTTS', 'Japanese Male Voice', 'male-japanese', 'Japanese', 'https://static.minimax.io/audio/speech-02/male-japanese.mp3', NULL, 6, NULL, NULL, NULL, NULL),
('TTS_MinimaxDoubleStreamTTS_0007', 'TTS_MinimaxDoubleStreamTTS', 'Korean Female Voice', 'female-korean', 'Korean', 'https://static.minimax.io/audio/speech-02/female-korean.mp3', NULL, 7, NULL, NULL, NULL, NULL),
('TTS_MinimaxDoubleStreamTTS_0008', 'TTS_MinimaxDoubleStreamTTS', 'Korean Male Voice', 'male-korean', 'Korean', 'https://static.minimax.io/audio/speech-02/male-korean.mp3', NULL, 8, NULL, NULL, NULL, NULL),
('TTS_MinimaxDoubleStreamTTS_0009', 'TTS_MinimaxDoubleStreamTTS', 'French Female Voice', 'female-french', 'French', 'https://static.minimax.io/audio/speech-02/female-french.mp3', NULL, 9, NULL, NULL, NULL, NULL),
('TTS_MinimaxDoubleStreamTTS_0010', 'TTS_MinimaxDoubleStreamTTS', 'French Male Voice', 'male-french', 'French', 'https://static.minimax.io/audio/speech-02/male-french.mp3', NULL, 10, NULL, NULL, NULL, NULL);"

execute_mysql "$VOICES_SQL" "Adding voice options (10 voices across 5 languages)"

# 6. Add entry to Liquibase changelog tracking
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
'202507021545-script', 
'setup-script', 
'setup-minimax-double-stream-db.sh', 
NOW(), 
(SELECT COALESCE(MAX(ORDEREXECUTED), 0) + 1 FROM DATABASECHANGELOG d), 
'EXECUTED', 
'8:script_insert', 
'MiniMax Double Stream TTS Provider via Script', 
'Automated setup via shell script', 
NULL, 
'4.20.0', 
NULL, 
NULL, 
CONCAT('script_', UNIX_TIMESTAMP())
);"

execute_mysql "$LIQUIBASE_SQL" "Updating Liquibase changelog tracking"

# 7. Verification
echo "🔍 Verifying installation..."

VERIFY_PROVIDER="SELECT id, name, provider_code FROM ai_model_provider WHERE provider_code = 'minimax_double_stream';"
echo "📋 Checking provider installation:"
docker exec $DB_CONTAINER mysql -u $DB_USER -p$DB_PASSWORD $MYSQL_CHARSET $DB_NAME -e "$VERIFY_PROVIDER"

VERIFY_VOICES="SELECT COUNT(*) as voice_count FROM ai_tts_voice WHERE tts_model_id = 'TTS_MinimaxDoubleStreamTTS';"
echo "🎤 Checking voice count:"
docker exec $DB_CONTAINER mysql -u $DB_USER -p$DB_PASSWORD $MYSQL_CHARSET $DB_NAME -e "$VERIFY_VOICES"

echo ""
echo "🎉 MiniMax Double Stream TTS Configuration Complete!"
echo "=================================================="
echo ""
echo "📋 Next Steps:"
echo "1. Restart the web container:"
echo "   docker restart xiaozhi-esp32-server-web"
echo ""
echo "2. Access the management interface:"
echo "   http://localhost:8002"
echo ""
echo "3. Configure MiniMax credentials:"
echo "   - Navigate to Model Configuration → TTS Settings"
echo "   - Find 'MiniMax Double Stream TTS'"
echo "   - Enter your Group ID and API Key"
echo "   - Select preferred voice and model settings"
echo ""
echo "4. The minimax_double_stream.py provider is ready for use!"
echo ""
echo "🔗 Documentation: https://www.minimax.io/platform/document/T2A%20V2"
echo ""