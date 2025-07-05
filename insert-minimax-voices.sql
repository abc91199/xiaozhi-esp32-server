SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
SET character_set_client = utf8mb4;
SET character_set_connection = utf8mb4;
SET character_set_results = utf8mb4;

-- Insert MiniMax TTS voices with proper encoding
INSERT INTO `ai_tts_voice` (`id`, `tts_model_id`, `name`, `tts_voice`, `languages`, `voice_demo`, `remark`, `sort`, `creator`, `create_date`, `updater`, `update_date`) VALUES
('TTS_MinimaxTTS_0001', 'TTS_MinimaxTTS', '少女音色', 'female-shaonv', '中文', 'https://static.minimax.io/audio/speech-02/female-shaonv.mp3', NULL, 1, NULL, NULL, NULL, NULL),
('TTS_MinimaxTTS_0002', 'TTS_MinimaxTTS', '青年男声', 'male-qingnian', '中文', 'https://static.minimax.io/audio/speech-02/male-qingnian.mp3', NULL, 2, NULL, NULL, NULL, NULL),
('TTS_MinimaxTTS_0003', 'TTS_MinimaxTTS', '温柔女声', 'female-wenrou', '中文', 'https://static.minimax.io/audio/speech-02/female-wenrou.mp3', NULL, 3, NULL, NULL, NULL, NULL),
('TTS_MinimaxTTS_0004', 'TTS_MinimaxTTS', '成熟男声', 'male-chengshu', '中文', 'https://static.minimax.io/audio/speech-02/male-chengshu.mp3', NULL, 4, NULL, NULL, NULL, NULL),
('TTS_MinimaxTTS_0005', 'TTS_MinimaxTTS', '英文女声', 'female-english', '英文', 'https://static.minimax.io/audio/speech-02/female-english.mp3', NULL, 5, NULL, NULL, NULL, NULL);