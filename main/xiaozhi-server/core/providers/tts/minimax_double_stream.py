import os
import uuid
import json
import queue
import asyncio
import traceback
import websockets
import requests
from core.utils.tts import MarkdownCleaner
from config.logger import setup_logging
from core.utils import opus_encoder_utils
from core.utils.util import check_model_key
from core.providers.tts.base import TTSProviderBase
from core.handle.abortHandle import handleAbortMessage
from core.providers.tts.dto.dto import SentenceType, ContentType, InterfaceType
from asyncio import Task


TAG = __name__
logger = setup_logging()


class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.ws = None
        self.interface_type = InterfaceType.DUAL_STREAM
        self._monitor_task = None  # 监听任务引用
        
        # MiniMax API 配置
        self.group_id = config.get("group_id")
        self.api_key = config.get("api_key")
        self.model = config.get("model", "speech-02-turbo")
        
        if config.get("private_voice"):
            self.voice = config.get("private_voice")
        else:
            self.voice = config.get("voice_id", "female-shaonv")
            
        # 语音设置
        default_voice_setting = {
            "voice_id": self.voice,
            "speed": 1,
            "vol": 1,
            "pitch": 0,
            "emotion": "happy",
        }
        self.voice_setting = {
            **default_voice_setting,
            **config.get("voice_setting", {}),
        }
        
        # 音频设置
        default_audio_setting = {
            "sample_rate": 16000,  # 优化为16kHz适配ESP32
            "bitrate": 128000,
            "format": "pcm",  # 使用PCM格式支持实时流式处理
            "channel": 1,
        }
        self.audio_setting = {
            **default_audio_setting, 
            **config.get("audio_setting", {})
        }
        
        # API URLs
        self.host = config.get("host", "api.minimax.io")
        self.ws_url = f"wss://{self.host}/ws/v1/t2a_v2"
        
        self.header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        self.enable_two_way = True
        self.tts_text = ""
        self.session_id = None
        
        # Opus编码器配置
        self.opus_encoder = opus_encoder_utils.OpusEncoderUtils(
            sample_rate=16000, channels=1, frame_size_ms=60
        )
        
        model_key_msg = check_model_key("TTS", self.api_key)
        if model_key_msg:
            logger.bind(tag=TAG).error(model_key_msg)

    async def open_audio_channels(self, conn):
        try:
            await super().open_audio_channels(conn)
        except Exception as e:
            logger.bind(tag=TAG).error(f"Failed to open audio channels: {str(e)}")
            self.ws = None
            raise

    async def _prepare_websocket_url(self):
        """准备WebSocket连接URL"""
        # MiniMax WebSocket API直接使用API key进行认证，无需预先创建token
        # URL已在初始化时设置
        return True

    async def _ensure_connection(self):
        """建立新的WebSocket连接"""
        try:
            logger.bind(tag=TAG).info("开始建立MiniMax WebSocket连接...")
            
            # 使用API key进行认证
            ws_headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            self.ws = await websockets.connect(
                self.ws_url, 
                additional_headers=ws_headers,
                max_size=1000000000
            )
            
            # 等待连接成功响应
            response = await self.ws.recv()
            result = json.loads(response)
            
            if result.get("event") == "connected_success":
                self.session_id = result.get("session_id")
                logger.bind(tag=TAG).info(f"MiniMax WebSocket连接建立成功，会话ID: {self.session_id}")
                return self.ws
            else:
                logger.bind(tag=TAG).error(f"WebSocket连接失败: {result}")
                return None
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"建立WebSocket连接失败: {str(e)}")
            self.ws = None
            raise

    def tts_text_priority_thread(self):
        """MiniMax双流式TTS的文本处理线程"""
        session_started = False
        pending_texts = []
        
        while not self.conn.stop_event.is_set():
            try:
                message = self.tts_text_queue.get(timeout=1)
                logger.bind(tag=TAG).debug(
                    f"收到TTS任务｜{message.sentence_type.name} ｜ {message.content_type.name} | 会话ID: {getattr(self.conn, 'sentence_id', 'None')}"
                )
                
                if self.conn.client_abort:
                    logger.bind(tag=TAG).info("收到打断信息，终止TTS文本处理线程")
                    continue

                if message.sentence_type == SentenceType.FIRST:
                    # 初始化参数
                    try:
                        if not getattr(self.conn, "sentence_id", None): 
                            self.conn.sentence_id = uuid.uuid4().hex
                            logger.bind(tag=TAG).info(f"自动生成新的会话ID: {self.conn.sentence_id}")

                        logger.bind(tag=TAG).info("开始启动MiniMax TTS会话...")
                        future = asyncio.run_coroutine_threadsafe(
                            self.start_session(self.conn.sentence_id),
                            loop=self.conn.loop,
                        )
                        future.result()
                        session_started = True
                        pending_texts = []
                        self.tts_audio_first_sentence = True
                        self.before_stop_play_files.clear()
                        logger.bind(tag=TAG).info("MiniMax TTS会话启动成功")
                    except Exception as e:
                        logger.bind(tag=TAG).error(f"启动TTS会话失败: {str(e)}")
                        session_started = False
                        continue

                elif ContentType.TEXT == message.content_type:
                    if message.content_detail:
                        # 收集文本，但不立即发送，避免重复
                        pending_texts.append(message.content_detail)
                        logger.bind(tag=TAG).info(f"📝 收集文本片段: {message.content_detail}")
                        logger.bind(tag=TAG).info(f"📝 当前收集的文本: {len(pending_texts)} 个片段")

                elif ContentType.FILE == message.content_type:
                    logger.bind(tag=TAG).info(
                        f"添加音频文件到待播放列表: {message.content_file}"
                    )
                    self.before_stop_play_files.append(
                        (message.content_file, message.content_detail)
                    )

                if message.sentence_type == SentenceType.LAST:
                    try:
                        # 发送所有待发送的文本
                        if session_started and pending_texts:
                            combined_text = "".join(pending_texts)
                            logger.bind(tag=TAG).info(f"📤 发送最终合并文本: '{combined_text[:100]}...'")
                            future = asyncio.run_coroutine_threadsafe(
                                self.text_to_speak(combined_text, None),
                                loop=self.conn.loop,
                            )
                            future.result()
                            logger.bind(tag=TAG).info("✅ 最终合并文本发送成功")
                        
                        logger.bind(tag=TAG).info("🏁 开始结束MiniMax TTS会话...")
                        future = asyncio.run_coroutine_threadsafe(
                            self.finish_session(self.conn.sentence_id),
                            loop=self.conn.loop,
                        )
                        future.result()
                        logger.bind(tag=TAG).info("✅ MiniMax TTS会话结束完成")
                        session_started = False
                        pending_texts = []
                    except Exception as e:
                        logger.bind(tag=TAG).error(f"结束TTS会话失败: {str(e)}")
                        session_started = False
                        continue

            except queue.Empty:
                continue
            except Exception as e:
                logger.bind(tag=TAG).error(
                    f"处理TTS文本失败: {str(e)}, 类型: {type(e).__name__}, 堆栈: {traceback.format_exc()}"
                )
                continue

    async def text_to_speak(self, text, _):
        """发送文本到TTS服务"""
        try:
            if self.ws is None:
                logger.bind(tag=TAG).warning(f"WebSocket连接不存在，终止发送文本")
                return

            # 过滤Markdown
            filtered_text = MarkdownCleaner.clean_markdown(text)

            # 发送task_continue事件
            await self._send_task_continue(filtered_text)
            return
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"发送TTS文本失败: {str(e)}")
            if self.ws:
                try:
                    await self.ws.close()
                except:
                    pass
                self.ws = None
            raise

    async def _send_task_continue(self, text):
        """发送task_continue事件"""
        try:
            task_continue_msg = {
                "event": "task_continue",
                "text": text
            }
            
            await self.ws.send(json.dumps(task_continue_msg))
            logger.bind(tag=TAG).debug(f"发送task_continue: {text[:50]}...")
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"发送task_continue失败: {str(e)}")
            raise

    async def _send_task_finish(self):
        """发送task_finish事件"""
        try:
            task_finish_msg = {
                "event": "task_finish"
            }
            
            await self.ws.send(json.dumps(task_finish_msg))
            logger.bind(tag=TAG).info("发送task_finish事件")
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"发送task_finish失败: {str(e)}")
            raise

    async def start_session(self, session_id):
        logger.bind(tag=TAG).info(f"开始MiniMax会话～～{session_id}")
        try:
            # 停止之前的监听任务
            task = self._monitor_task
            if (
                task is not None
                and isinstance(task, Task)
                and not task.done()
            ):
                logger.bind(tag=TAG).info("等待上一个监听任务结束...")
                if self.ws is not None:
                    logger.bind(tag=TAG).info("强制关闭上一个WebSocket连接...")
                    try:
                        await self.ws.close()
                    except Exception as e:
                        logger.bind(tag=TAG).warning(f"关闭上一个ws异常: {e}")
                    self.ws = None
                try:
                    await asyncio.wait_for(task, timeout=8)
                except Exception as e:
                    logger.bind(tag=TAG).warning(f"等待监听任务异常: {e}")
                self._monitor_task = None

            # 准备WebSocket连接
            if not await self._prepare_websocket_url():
                raise Exception("准备WebSocket URL失败")
                
            await self._ensure_connection()

            # 遵循Huoshan模式：不重置编码器状态，保持连续性
            logger.bind(tag=TAG).info("🔄 OPUS编码器: 新会话开始，保持编码器状态连续性")

            # 发送task_start事件
            await self._send_task_start()

            # 启动监听任务
            self._monitor_task = asyncio.create_task(self._start_monitor_tts_response())

            logger.bind(tag=TAG).info("MiniMax会话启动成功")
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"启动会话失败: {str(e)}")
            # 确保清理资源
            if hasattr(self, "_monitor_task"):
                try:
                    self._monitor_task.cancel()
                    await self._monitor_task
                except:
                    pass
                self._monitor_task = None
            if self.ws:
                try:
                    await self.ws.close()
                except:
                    pass
                self.ws = None
            raise

    async def _send_task_start(self):
        """发送task_start事件"""
        try:
            task_start_msg = {
                "event": "task_start",
                "model": self.model,
                "voice_setting": self.voice_setting,
                "audio_setting": self.audio_setting,
                "language_boost": "Chinese,Yue"
            }
            
            await self.ws.send(json.dumps(task_start_msg))
            
            # 等待task_started响应
            response = await self.ws.recv()
            result = json.loads(response)
            
            if result.get("event") == "task_started":
                logger.bind(tag=TAG).info("MiniMax任务启动成功")
                return True
            else:
                logger.bind(tag=TAG).error(f"任务启动失败: {result}")
                return False
                
        except Exception as e:
            logger.bind(tag=TAG).error(f"发送task_start失败: {str(e)}")
            return False

    async def finish_session(self, session_id):
        logger.bind(tag=TAG).info(f"关闭MiniMax会话～～{session_id}")
        try:
            if self.ws:
                # 发送task_finish事件
                await self._send_task_finish()
                logger.bind(tag=TAG).info("已发送task_finish，等待监听任务完成")
                
                # 遵循Huoshan模式：等待监听任务完成（监听任务会处理完成逻辑）
                if hasattr(self, "_monitor_task") and self._monitor_task:
                    try:
                        await self._monitor_task
                        logger.bind(tag=TAG).info("监听任务正常完成")
                    except Exception as e:
                        logger.bind(tag=TAG).error(
                            f"等待监听任务完成时发生错误: {str(e)}"
                        )
                    finally:
                        self._monitor_task = None

                # 关闭连接
                await self.close()
                
                # 遵循Huoshan模式：不重置编码器状态
                logger.bind(tag=TAG).info("🔄 OPUS编码器: 会话正常结束，保持编码器状态")
                
        except Exception as e:
            logger.bind(tag=TAG).error(f"关闭会话失败: {str(e)}")
            # 确保清理资源
            if hasattr(self, "_monitor_task"):
                try:
                    self._monitor_task.cancel()
                    await self._monitor_task
                except:
                    pass
                self._monitor_task = None
            if self.ws:
                try:
                    await self.ws.close()
                except:
                    pass
                self.ws = None
            
            # 遵循Huoshan模式：错误处理中也不重置编码器状态
            logger.bind(tag=TAG).info("🔄 OPUS编码器: 错误处理完成，保持编码器状态")
            raise

    async def close(self):
        """资源清理方法"""
        if self.ws:
            try:
                await self.ws.close()
            except:
                pass
            self.ws = None

    async def _start_monitor_tts_response(self):
        """监听MiniMax TTS响应"""
        opus_datas_cache = []  # 遵循Huoshan模式：使用缓存
        is_first_sentence = True
        first_sentence_segment_count = 0
        received_audio = False
        chunk_count = 0
        current_text_first_chunk = True  # 跟踪当前文本段的第一个块
        
        try:
            logger.bind(tag=TAG).info("🎧 监听开始: MiniMax WebSocket响应监听启动")
            while not self.conn.stop_event.is_set():
                try:
                    msg = await self.ws.recv()
                    
                    # 检查客户端是否中止
                    if self.conn.client_abort:
                        logger.bind(tag=TAG).info("收到打断信息，终止监听TTS响应")
                        break

                    # 解析JSON响应
                    try:
                        json_msg = json.loads(msg)
                        event_type = json_msg.get("event", "")
                        logger.bind(tag=TAG).info(f"📨 WEBSOCKET事件: 收到 {event_type}")
                        
                        if event_type == "task_continued":
                            # 检查是否是新文本段开始（第一个音频块）- 模拟Huoshan的EVENT_TTSSentenceStart
                            if "data" in json_msg and "audio" in json_msg["data"] and current_text_first_chunk:
                                logger.bind(tag=TAG).info("🎬 新文本段开始: 发送SentenceType.FIRST")
                                self.tts_audio_queue.put(
                                    (SentenceType.FIRST, [], None)
                                )
                                logger.bind(tag=TAG).info("✅ 队列操作: SentenceType.FIRST 已排队")
                                # 重置缓存和计数器（如Huoshan line 435-436）
                                opus_datas_cache = []
                                first_sentence_segment_count = 0
                                current_text_first_chunk = False
                            
                            if "data" in json_msg and "audio" in json_msg["data"]:
                                audio_hex = json_msg["data"]["audio"]
                                chunk_count += 1
                                logger.bind(tag=TAG).info(f"🎧 WEBSOCKET音频: 收到音频块 #{chunk_count}，hex长度: {len(audio_hex)} 字符")
                                received_audio = True
                                
                                # 检查是否为最终块 - 只检查一次避免重复
                                is_final_chunk = json_msg.get("is_final", False)
                                logger.bind(tag=TAG).info(f"🔍 Final检查: 块#{chunk_count} is_final={is_final_chunk}")
                                
                                # 只处理有内容的音频块
                                if audio_hex:
                                    audio_bytes = bytes.fromhex(audio_hex)
                                    logger.bind(tag=TAG).info(f"📥 PCM转换: 块#{chunk_count} - {len(audio_bytes)} 字节PCM")
                                    
                                    opus_datas = self._convert_pcm_chunk(audio_bytes)
                                    logger.bind(tag=TAG).info(f"🎵 Opus转换: 块#{chunk_count} 转换为 {len(opus_datas)} 个Opus包")
                                    
                                    if opus_datas:
                                        if is_first_sentence:
                                            first_sentence_segment_count += 1
                                            if first_sentence_segment_count <= 6:
                                                # 前6个片段立即播放
                                                logger.bind(tag=TAG).info(f"🎵 立即播放: 第一句前6个片段 #{first_sentence_segment_count}")
                                                self.tts_audio_queue.put(
                                                    (SentenceType.MIDDLE, opus_datas, None)
                                                )
                                                logger.bind(tag=TAG).info(f"✅ 队列操作: MIDDLE #{first_sentence_segment_count} 已排队（立即播放）")
                                            else:
                                                # 后续片段缓存
                                                logger.bind(tag=TAG).info(f"📦 缓存音频: 第一句后续片段 #{first_sentence_segment_count}")
                                                opus_datas_cache = opus_datas_cache + opus_datas
                                                logger.bind(tag=TAG).info(f"📦 缓存状态: 缓存中有 {len(opus_datas_cache)} 个包")
                                        else:
                                            # 非第一句：全部缓存
                                            logger.bind(tag=TAG).info(f"📦 缓存音频: 后续句子片段")
                                            opus_datas_cache = opus_datas_cache + opus_datas
                                            logger.bind(tag=TAG).info(f"📦 缓存状态: 缓存中有 {len(opus_datas_cache)} 个包")
                                else:
                                    logger.bind(tag=TAG).warning(f"⚠️ 空音频: 块#{chunk_count} audio_hex为空，但继续处理final检查")
                                
                                # 检查是否为最终响应 - 相当于Huoshan的EVENT_TTSSentenceEnd
                                if is_final_chunk:
                                    logger.bind(tag=TAG).info("🏁 FINAL块处理: 收到最终音频响应标记 (is_final=true) - 文本段结束")
                                    
                                    # 决定是否释放缓存
                                    should_release_cache = not is_first_sentence or first_sentence_segment_count > 10
                                    logger.bind(tag=TAG).info(f"🔍 缓存决策: is_first_sentence={is_first_sentence}, segment_count={first_sentence_segment_count}, should_release={should_release_cache}")
                                    
                                    if should_release_cache and opus_datas_cache:
                                        logger.bind(tag=TAG).info(f"🎵 释放缓存: 释放 {len(opus_datas_cache)} 个Opus包")
                                        self.tts_audio_queue.put(
                                            (SentenceType.MIDDLE, opus_datas_cache, None)
                                        )
                                        logger.bind(tag=TAG).info("✅ 队列操作: 缓存的MIDDLE已排队（释放缓存）")
                                        opus_datas_cache = []  # 清空缓存
                                        logger.bind(tag=TAG).info("🗑️ 缓存清理: 缓存已清空")
                                    
                                    # 重置状态为下一个文本段做准备
                                    is_first_sentence = False
                                    current_text_first_chunk = True
                                    chunk_count = 0
                                    logger.bind(tag=TAG).info("🔄 状态重置: 为下一个文本段重置状态")
                            else:
                                logger.bind(tag=TAG).warning(f"⚠️ 无音频数据: task_continued 但无音频数据! 消息: {json_msg}")
                                # 检查无音频数据的情况下是否为最终响应
                                if json_msg.get("is_final", False):
                                    logger.bind(tag=TAG).info("🏁 FINAL处理: 收到最终响应标记但无音频数据")
                                    # 处理完成逻辑
                                    is_first_sentence = False
                                    current_text_first_chunk = True
                                    chunk_count = 0
                            
                        elif event_type == "task_finished":
                            logger.bind(tag=TAG).info(f"✅ 完全结束: WEBSOCKET API完全结束 - 总共接收 {chunk_count} 个音频块")
                            logger.bind(tag=TAG).info("🎬 会话结束: MiniMax模式，音频已通过缓存机制处理完成")
                            # MiniMax与Huoshan不同：音频已通过is_final缓存释放机制处理，不需要额外处理
                            # 只发送LAST信号标识会话结束
                            self.tts_audio_queue.put((SentenceType.LAST, [], None))
                            logger.bind(tag=TAG).info("✅ 完成处理: 仅发送LAST信号，不重复处理音频")
                            break
                            
                        elif event_type == "task_failed":
                            error_msg = json_msg.get("base_resp", {}).get("status_msg", "Unknown error")
                            logger.bind(tag=TAG).error(f"TTS任务失败: {error_msg}")
                            break
                            
                    except json.JSONDecodeError:
                        logger.bind(tag=TAG).warning(f"JSON解析失败: 无法解析消息 {msg}")
                        
                except websockets.ConnectionClosed:
                    logger.bind(tag=TAG).warning("WebSocket连接已关闭")
                    break
                except Exception as e:
                    logger.bind(tag=TAG).error(
                        f"监听异常: {e}"
                    )
                    traceback.print_exc()
                    break
                    
        finally:
            logger.bind(tag=TAG).info("🔚 监听结束: WebSocket监听任务完全结束，清理引用")
            # 监听任务退出时清理引用
            self._monitor_task = None

    def _convert_pcm_chunk(self, pcm_data):
        """将PCM音频块直接转换为Opus编码，保持音频连续性"""
        try:
            if not pcm_data or len(pcm_data) == 0:
                logger.bind(tag=TAG).warning("⚠️ PCM转换: 输入数据为空")
                return []
            
            logger.bind(tag=TAG).info(f"🔄 PCM转换: 开始处理 {len(pcm_data)} 字节PCM数据")
            
            # 确保数据长度是2的倍数（16bit样本）
            if len(pcm_data) % 2 != 0:
                pcm_data = pcm_data[:-1]
                logger.bind(tag=TAG).debug(f"PCM对齐: 调整长度为 {len(pcm_data)} 字节")
            
            # 保持编码器连续性，只有当有足够数据生成完整帧时才输出
            try:
                # 正常添加数据，让编码器自然输出完整帧
                opus_packets = self.opus_encoder.encode_pcm_to_opus(pcm_data, False)
                
                logger.bind(tag=TAG).info(f"✅ PCM转换: {len(pcm_data)} 字节PCM → {len(opus_packets)} 个Opus包 (连续输出)")
                return opus_packets
                
            except Exception as e:
                logger.bind(tag=TAG).error(f"❌ Opus编码失败: {str(e)}")
                return []
                
        except Exception as e:
            logger.bind(tag=TAG).error(f"❌ PCM音频转换失败: {str(e)}")
            return []

    def wav_to_opus_data_audio_raw(self, raw_data_var, is_end=False):
        """将音频数据转换为Opus编码"""
        try:
            if not raw_data_var:
                return []
                
            # 保存到临时文件进行转换
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(raw_data_var)
                temp_file_path = temp_file.name
            
            try:
                # 使用现有的音频转换工具
                from core.utils.util import audio_to_data
                audio_datas, _ = audio_to_data(temp_file_path, is_opus=True)
                return audio_datas
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    
        except Exception as e:
            logger.bind(tag=TAG).error(f"音频转换失败: {str(e)}")
            return []

    def to_tts(self, text: str) -> list:
        """非流式生成音频数据，用于生成音频及测试场景"""
        try:
            # 创建事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # 存储音频数据
            audio_data = []

            async def _generate_audio():
                # 准备WebSocket URL
                if not await self._prepare_websocket_url():
                    raise Exception("准备WebSocket URL失败")
                    
                # 建立WebSocket连接
                await self._ensure_connection()

                try:
                    # 发送task_start
                    if not await self._send_task_start():
                        raise Exception("启动任务失败")
                    
                    # 发送文本
                    await self._send_task_continue(text)
                    
                    # 发送结束信号
                    await self._send_task_finish()

                    # 接收音频数据
                    while True:
                        msg = await self.ws.recv()
                        
                        try:
                            json_msg = json.loads(msg)
                            event_type = json_msg.get("event", "")
                            
                            if event_type == "task_continued":
                                if "data" in json_msg and "audio" in json_msg["data"]:
                                    audio_hex = json_msg["data"]["audio"]
                                    audio_bytes = bytes.fromhex(audio_hex)
                                    opus_datas = self._convert_pcm_chunk(audio_bytes)
                                    audio_data.extend(opus_datas)
                                    
                            elif event_type == "task_finished":
                                break
                            elif event_type == "task_failed":
                                raise Exception(f"任务失败: {json_msg}")
                                
                        except json.JSONDecodeError:
                            logger.bind(tag=TAG).warning(f"无法解析响应: {msg}")

                finally:
                    # 清理资源
                    try:
                        await self.ws.close()
                    except:
                        pass
                    self.ws = None

            # 运行异步任务
            loop.run_until_complete(_generate_audio())
            loop.close()

            return audio_data

        except Exception as e:
            logger.bind(tag=TAG).error(f"生成音频数据失败: {str(e)}")
            return []