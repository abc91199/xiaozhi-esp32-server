-- Fix MiniMax TTS Provider Unicode Encoding Issues
SET NAMES utf8mb4;
SET character_set_client = utf8mb4;
SET character_set_connection = utf8mb4;
SET character_set_results = utf8mb4;

-- Update provider with proper Unicode
UPDATE `ai_model_provider` SET 
`name` = 'MiniMax语音合成'
WHERE `id` = 'SYSTEM_TTS_Minimax';

-- Update model config with proper Unicode
UPDATE `ai_model_config` SET 
`model_code` = 'MiniMax语音合成',
`remark` = 'MiniMax Speech-02标准语音合成配置说明：
1. 访问 https://www.minimax.io/ 注册并开通MiniMax账号
2. 获取GroupId和API Key
3. 推荐使用speech-02-turbo模型以获得更好的性能
4. 支持超过30种语言和300+音色
5. 支持发音字典和音色混合功能
6. 标准HTTP API调用，适合批量处理
7. 填入配置文件中'
WHERE `id` = 'TTS_MinimaxTTS';

-- Update voice names with proper Unicode
UPDATE `ai_tts_voice` SET `name` = '少女音色' WHERE `id` = 'TTS_MinimaxTTS_0001';
UPDATE `ai_tts_voice` SET `name` = '青年男声' WHERE `id` = 'TTS_MinimaxTTS_0002';
UPDATE `ai_tts_voice` SET `name` = '温柔女声' WHERE `id` = 'TTS_MinimaxTTS_0003';
UPDATE `ai_tts_voice` SET `name` = '成熟男声' WHERE `id` = 'TTS_MinimaxTTS_0004';
UPDATE `ai_tts_voice` SET `name` = '英文女声' WHERE `id` = 'TTS_MinimaxTTS_0005';

-- Update language names with proper Unicode
UPDATE `ai_tts_voice` SET `languages` = '中文' WHERE `tts_model_id` = 'TTS_MinimaxTTS' AND `languages` = '中文';
UPDATE `ai_tts_voice` SET `languages` = '英文' WHERE `tts_model_id` = 'TTS_MinimaxTTS' AND `languages` = '英文';