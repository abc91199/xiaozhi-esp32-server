SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
SET character_set_client = utf8mb4;
SET character_set_connection = utf8mb4;
SET character_set_results = utf8mb4;

-- Fix provider fields JSON with proper Unicode
UPDATE `ai_model_provider` SET 
`fields` = '[
  {"key":"group_id","label":"组ID","type":"string"},
  {"key":"api_key","label":"API密钥","type":"string"},
  {"key":"model","label":"模型","type":"string"},
  {"key":"voice_id","label":"默认音色","type":"string"},
  {"key":"voice_setting","label":"语音设置","type":"dict","dict_name":"voice_setting"},
  {"key":"pronunciation_dict","label":"发音字典","type":"dict","dict_name":"pronunciation_dict"},
  {"key":"audio_setting","label":"音频设置","type":"dict","dict_name":"audio_setting"},
  {"key":"timber_weights","label":"音色权重","type":"string"}
]'
WHERE `id` = 'SYSTEM_TTS_Minimax';

-- Fix model config JSON with proper Unicode
UPDATE `ai_model_config` SET 
`config_json` = '{
  "type": "minimax",
  "group_id": "你的MiniMax组ID",
  "api_key": "你的MiniMax API密钥",
  "model": "speech-02-turbo",
  "voice_id": "female-shaonv",
  "voice_setting": {
    "voice_id": "female-shaonv",
    "speed": 1,
    "vol": 1,
    "pitch": 0,
    "emotion": "happy"
  },
  "pronunciation_dict": {
    "tone": [
      "处理/(chu3)(li3)",
      "危险/dangerous"
    ]
  },
  "audio_setting": {
    "sample_rate": 32000,
    "bitrate": 128000,
    "format": "mp3",
    "channel": 1
  },
  "timber_weights": ""
}'
WHERE `id` = 'TTS_MinimaxTTS';