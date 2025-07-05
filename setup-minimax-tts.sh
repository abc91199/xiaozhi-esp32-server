#!/bin/bash

# MiniMax TTS Provider Database Setup Script
# This script adds the original MiniMax TTS provider to the database

echo "Setting up MiniMax TTS Provider in database..."

# Database connection details
DB_HOST="localhost"
DB_PORT="3306"
DB_NAME="xiaozhi_db"
DB_USER="root"
DB_PASSWORD="123456"

# Connect to database and execute the SQL
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" << 'EOF'

-- 增加MiniMax标准TTS供应器和模型配置
DELETE FROM `ai_model_provider` WHERE id = 'SYSTEM_TTS_Minimax';
INSERT INTO `ai_model_provider` (`id`, `model_type`, `provider_code`, `name`, `fields`, `sort`, `creator`, `create_date`, `updater`, `update_date`) VALUES
('SYSTEM_TTS_Minimax', 'TTS', 'minimax', 'MiniMax语音合成', '[{"key":"group_id","label":"组ID","type":"string"},{"key":"api_key","label":"API密钥","type":"string"},{"key":"model","label":"模型","type":"string"},{"key":"voice_id","label":"默认音色","type":"string"},{"key":"voice_setting","label":"语音设置","type":"dict","dict_name":"voice_setting"},{"key":"pronunciation_dict","label":"发音字典","type":"dict","dict_name":"pronunciation_dict"},{"key":"audio_setting","label":"音频设置","type":"dict","dict_name":"audio_setting"},{"key":"timber_weights","label":"音色权重","type":"string"}]', 16, 1, NOW(), 1, NOW());

DELETE FROM `ai_model_config` WHERE id = 'TTS_MinimaxTTS';
INSERT INTO `ai_model_config` VALUES ('TTS_MinimaxTTS', 'TTS', 'MinimaxTTS', 'MiniMax语音合成', 0, 1, '{"type": "minimax", "group_id": "你的MiniMax组ID", "api_key": "你的MiniMax API密钥", "model": "speech-02-turbo", "voice_id": "female-shaonv", "voice_setting": {"voice_id": "female-shaonv", "speed": 1, "vol": 1, "pitch": 0, "emotion": "happy"}, "pronunciation_dict": {"tone": ["处理/(chu3)(li3)", "危险/dangerous"]}, "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1}, "timber_weights": ""}', NULL, NULL, 16, NULL, NULL, NULL, NULL);

-- MiniMax标准TTS模型配置说明文档
UPDATE `ai_model_config` SET 
`doc_link` = 'https://www.minimax.io/platform/document/T2A%20V2',
`remark` = 'MiniMax Speech-02标准语音合成配置说明：
1. 访问 https://www.minimax.io/ 注册并开通MiniMax账号
2. 获取GroupId和API Key
3. 推荐使用speech-02-turbo模型以获得更好的性能
4. 支持超过30种语言和300+音色
5. 支持发音字典和音色混合功能
6. 标准HTTP API调用，适合批量处理
7. 填入配置文件中' WHERE `id` = 'TTS_MinimaxTTS';

-- 添加MiniMax标准TTS音色
DELETE FROM `ai_tts_voice` WHERE tts_model_id = 'TTS_MinimaxTTS';
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0001', 'TTS_MinimaxTTS', '少女音色', 'female-shaonv', '中文', 'https://static.minimax.io/audio/speech-02/female-shaonv.mp3', NULL, 1, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0002', 'TTS_MinimaxTTS', '青年男声', 'male-qingnian', '中文', 'https://static.minimax.io/audio/speech-02/male-qingnian.mp3', NULL, 2, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0003', 'TTS_MinimaxTTS', '温柔女声', 'female-wenrou', '中文', 'https://static.minimax.io/audio/speech-02/female-wenrou.mp3', NULL, 3, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0004', 'TTS_MinimaxTTS', '成熟男声', 'male-chengshu', '中文', 'https://static.minimax.io/audio/speech-02/male-chengshu.mp3', NULL, 4, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0005', 'TTS_MinimaxTTS', '甜美女声', 'female-tianmei', '中文', 'https://static.minimax.io/audio/speech-02/female-tianmei.mp3', NULL, 5, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0006', 'TTS_MinimaxTTS', '磁性男声', 'male-cixing', '中文', 'https://static.minimax.io/audio/speech-02/male-cixing.mp3', NULL, 6, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0007', 'TTS_MinimaxTTS', '活力女声', 'female-huoli', '中文', 'https://static.minimax.io/audio/speech-02/female-huoli.mp3', NULL, 7, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0008', 'TTS_MinimaxTTS', '沉稳男声', 'male-chenwen', '中文', 'https://static.minimax.io/audio/speech-02/male-chenwen.mp3', NULL, 8, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0009', 'TTS_MinimaxTTS', '知性女声', 'female-zhixing', '中文', 'https://static.minimax.io/audio/speech-02/female-zhixing.mp3', NULL, 9, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0010', 'TTS_MinimaxTTS', '阳光男声', 'male-yangguang', '中文', 'https://static.minimax.io/audio/speech-02/male-yangguang.mp3', NULL, 10, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0011', 'TTS_MinimaxTTS', '英文女声', 'female-english', '英文', 'https://static.minimax.io/audio/speech-02/female-english.mp3', NULL, 11, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0012', 'TTS_MinimaxTTS', '英文男声', 'male-english', '英文', 'https://static.minimax.io/audio/speech-02/male-english.mp3', NULL, 12, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0013', 'TTS_MinimaxTTS', '日语女声', 'female-japanese', '日语', 'https://static.minimax.io/audio/speech-02/female-japanese.mp3', NULL, 13, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0014', 'TTS_MinimaxTTS', '日语男声', 'male-japanese', '日语', 'https://static.minimax.io/audio/speech-02/male-japanese.mp3', NULL, 14, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0015', 'TTS_MinimaxTTS', '韩语女声', 'female-korean', '韩语', 'https://static.minimax.io/audio/speech-02/female-korean.mp3', NULL, 15, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0016', 'TTS_MinimaxTTS', '韩语男声', 'male-korean', '韩语', 'https://static.minimax.io/audio/speech-02/male-korean.mp3', NULL, 16, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0017', 'TTS_MinimaxTTS', '法语女声', 'female-french', '法语', 'https://static.minimax.io/audio/speech-02/female-french.mp3', NULL, 17, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0018', 'TTS_MinimaxTTS', '法语男声', 'male-french', '法语', 'https://static.minimax.io/audio/speech-02/male-french.mp3', NULL, 18, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0019', 'TTS_MinimaxTTS', '德语女声', 'female-german', '德语', 'https://static.minimax.io/audio/speech-02/female-german.mp3', NULL, 19, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0020', 'TTS_MinimaxTTS', '德语男声', 'male-german', '德语', 'https://static.minimax.io/audio/speech-02/male-german.mp3', NULL, 20, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0021', 'TTS_MinimaxTTS', '西班牙语女声', 'female-spanish', '西班牙语', 'https://static.minimax.io/audio/speech-02/female-spanish.mp3', NULL, 21, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0022', 'TTS_MinimaxTTS', '西班牙语男声', 'male-spanish', '西班牙语', 'https://static.minimax.io/audio/speech-02/male-spanish.mp3', NULL, 22, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0023', 'TTS_MinimaxTTS', '意大利语女声', 'female-italian', '意大利语', 'https://static.minimax.io/audio/speech-02/female-italian.mp3', NULL, 23, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0024', 'TTS_MinimaxTTS', '意大利语男声', 'male-italian', '意大利语', 'https://static.minimax.io/audio/speech-02/male-italian.mp3', NULL, 24, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0025', 'TTS_MinimaxTTS', '葡萄牙语女声', 'female-portuguese', '葡萄牙语', 'https://static.minimax.io/audio/speech-02/female-portuguese.mp3', NULL, 25, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0026', 'TTS_MinimaxTTS', '葡萄牙语男声', 'male-portuguese', '葡萄牙语', 'https://static.minimax.io/audio/speech-02/male-portuguese.mp3', NULL, 26, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0027', 'TTS_MinimaxTTS', '俄语女声', 'female-russian', '俄语', 'https://static.minimax.io/audio/speech-02/female-russian.mp3', NULL, 27, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0028', 'TTS_MinimaxTTS', '俄语男声', 'male-russian', '俄语', 'https://static.minimax.io/audio/speech-02/male-russian.mp3', NULL, 28, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0029', 'TTS_MinimaxTTS', '阿拉伯语女声', 'female-arabic', '阿拉伯语', 'https://static.minimax.io/audio/speech-02/female-arabic.mp3', NULL, 29, NULL, NULL, NULL, NULL);
INSERT INTO `ai_tts_voice` VALUES ('TTS_MinimaxTTS_0030', 'TTS_MinimaxTTS', '阿拉伯语男声', 'male-arabic', '阿拉伯语', 'https://static.minimax.io/audio/speech-02/male-arabic.mp3', NULL, 30, NULL, NULL, NULL, NULL);

EOF

if [ $? -eq 0 ]; then
    echo "✅ MiniMax TTS Provider has been successfully added to the database!"
    echo ""
    echo "📋 Provider Details:"
    echo "   - Provider Code: minimax"
    echo "   - Provider Name: MiniMax语音合成"
    echo "   - Model ID: TTS_MinimaxTTS"
    echo "   - Model Name: MinimaxTTS"
    echo ""
    echo "🔧 Configuration Required:"
    echo "   - group_id: Your MiniMax Group ID"
    echo "   - api_key: Your MiniMax API Key"
    echo "   - model: speech-02-turbo (recommended)"
    echo "   - voice_id: female-shaonv (default)"
    echo ""
    echo "📚 Documentation: https://www.minimax.io/platform/document/T2A%20V2"
    echo ""
    echo "🎯 Next Steps:"
    echo "   1. Log into the XiaoZhi management panel"
    echo "   2. Go to Model Configuration → TTS Settings"
    echo "   3. Find 'MiniMax语音合成' provider"
    echo "   4. Configure your GroupId and API Key"
    echo "   5. Select your preferred voice and settings"
else
    echo "❌ Failed to add MiniMax TTS Provider to database"
    echo "Please check your database connection and credentials"
fi