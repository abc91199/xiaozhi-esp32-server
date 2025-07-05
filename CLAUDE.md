# XiaoZhi ESP32 Server - Project Understanding

## Project Overview

XiaoZhi ESP32 Server is a comprehensive open-source voice AI assistant backend service designed specifically for ESP32 hardware devices. It provides a complete ecosystem for building intelligent voice assistants with real-time audio processing, multi-modal AI integration, device management, and extensible plugin architecture.

**Primary Repository**: https://github.com/xinnan-tech/xiaozhi-esp32-server
**License**: MIT
**Languages**: Python (AI/WebSocket server), Java/Spring Boot (management API), Vue.js (web interface)

## Architecture Overview

### Three-Tier Architecture

1. **XiaoZhi Server** (Python/AsyncIO)
   - Real-time WebSocket communication with ESP32 devices
   - Audio processing pipeline (VAD, ASR, TTS)
   - AI service integration (LLM, Vision models)
   - Plugin and tool execution system

2. **Manager API** (Java/Spring Boot)
   - Device lifecycle management
   - User authentication and authorization
   - Configuration management
   - OTA (Over-The-Air) update coordination

3. **Manager Web** (Vue.js)
   - Web-based management dashboard
   - Device binding and configuration
   - User management interface
   - Real-time monitoring and control

## Core Components

### WebSocket Server (`main/xiaozhi-server/`)

**Main Entry Point**: `app.py`
- Starts WebSocket server on port 8000 (configurable)
- Starts HTTP server on port 8003 for OTA and vision APIs
- Manages graceful shutdown and resource cleanup

**Core Architecture**:
- `core/websocket_server.py` - Main WebSocket server
- `core/connection.py` - Individual client connection handler
- `core/handle/` - Message processing handlers
- `core/providers/` - Modular AI service providers
- `core/utils/` - Utility functions and helpers

### Manager API (`main/manager-api/`)

**Main Entry Point**: `src/main/java/xiaozhi/AdminApplication.java`
- Spring Boot application on port 8002
- Provides REST APIs for device and user management
- Database integration with MySQL and Redis
- JWT-based authentication system

**Key Modules**:
- `modules/device/` - Device registration and management
- `modules/agent/` - AI agent configuration
- `modules/model/` - AI model provider management
- `modules/security/` - Authentication and authorization
- `modules/sys/` - System administration

### Manager Web (`main/manager-web/`)

**Main Entry Point**: `src/main.js`
- Vue.js 2 application with Element UI
- Progressive Web App (PWA) capabilities
- Real-time dashboard for device management
- Model configuration and user administration

## Audio Processing Pipeline

### Real-time Voice Processing

1. **Voice Activity Detection (VAD)**
   - Uses Silero VAD model for real-time voice detection
   - Configurable threshold and silence duration
   - Automatic conversation flow control

2. **Automatic Speech Recognition (ASR)**
   - Multiple provider support: FunASR, Doubao, Tencent, Aliyun, Baidu
   - Streaming and batch processing modes
   - Hot word and correction table support

3. **Large Language Models (LLM)**
   - OpenAI-compatible API integration
   - Supported providers: ChatGLM, Doubao, DeepSeek, Gemini, Ollama, Dify
   - Function calling and tool integration
   - Streaming response support

4. **Text-to-Speech (TTS)**
   - Multiple provider support: Edge TTS, Doubao, GPT-SoVITS, Fish Speech
   - Streaming synthesis for low latency
   - Custom voice training support
   - Opus audio encoding for ESP32 optimization

### Audio Format Specifications

- **Input**: Opus-encoded, 16kHz, mono, 60ms frames
- **Processing**: PCM conversion for AI services
- **Output**: Opus-encoded audio chunks
- **Bandwidth**: ~24kbps (optimized for ESP32)

## ESP32 Hardware Integration

### Communication Protocol

**WebSocket Connection**:
- Primary endpoint: `ws://server:8000/xiaozhi/v1/`
- Binary audio data transmission
- JSON control messages
- Real-time bidirectional communication

**Device Authentication**:
- MAC address-based device identification
- Optional Bearer token authentication
- Device whitelist support
- 6-digit activation code binding process

### Device Registration Flow

1. ESP32 sends hardware info to `/ota/` endpoint
2. Server generates 6-digit activation code
3. User enters code in management panel
4. Device receives WebSocket URL and connects
5. Persistent connection established for voice interaction

### OTA Update System

**Update Process**:
- Automatic version checking
- Board type compatibility validation
- Secure download URL generation
- Conditional updates based on device settings

**Supported ESP32 Variants**:
- ESP32 (original)
- ESP32-S3 (with AI acceleration)
- Custom board types

## AI Service Integration

### Modular Provider System

**Base Classes**:
- `ASRProviderBase` - Speech recognition interface
- `LLMProviderBase` - Language model interface
- `TTSProviderBase` - Text-to-speech interface
- `VLLMProviderBase` - Vision language model interface

**Configuration-Driven Selection**:
```yaml
selected_module:
  VAD: SileroVAD
  ASR: FunASR
  LLM: ChatGLMLLM
  VLLM: ChatGLMVLLM
  TTS: EdgeTTS
  Memory: nomem
  Intent: function_call
```

### Memory Management

**Memory Types**:
- `nomem` - No persistent memory
- `mem_local_short` - Local conversation summarization
- `mem0ai` - External memory service integration

**Memory Features**:
- Context-aware conversation history
- Automatic memory summarization
- Multi-user memory isolation

### Intent Recognition and Function Calling

**Intent Types**:
- `nointent` - Basic conversation only
- `intent_llm` - LLM-based intent classification
- `function_call` - Direct function calling with streaming

**Built-in Functions**:
- Weather information (`get_weather`)
- News retrieval (`get_news_from_chinanews`, `get_news_from_newsnow`)
- Music playback (`play_music`)
- Home Assistant integration (`hass_get_state`, `hass_set_state`)
- Agent role switching (`change_role`)

## Plugin and Tool System

### Unified Tool Handler

**Tool Executors**:
- Server Plugin Executor - Local function plugins
- Server MCP Executor - Model Context Protocol integration
- Device IoT Executor - ESP32 device control
- Device MCP Executor - Device-side MCP client
- MCP Endpoint Executor - External MCP services

### MCP (Model Context Protocol) Integration

**Three Integration Types**:

1. **Device-side MCP Client**: ESP32 devices act as MCP clients
2. **Server-side MCP Integration**: Server connects to MCP services
3. **MCP Endpoint Integration**: WebSocket-based MCP endpoints

**Capabilities**:
- Tool discovery and execution
- Resource management
- Vision analysis with JWT authentication
- Bidirectional communication

#### MCP Server Function Implementation Details

The XiaoZhi ESP32 Server implements a sophisticated MCP (Model Context Protocol) architecture that provides seamless integration with external tools and services through three distinct integration patterns.

##### Architecture Components

**Core MCP System Files**:
- `core/providers/tools/unified_tool_handler.py` - Central coordinator for all MCP executors
- `core/providers/tools/base/tool_types.py` - Defines MCP tool type enumerations
- `mcp_server_settings.json` - Configuration template for MCP services

**Server-side MCP Implementation** (`core/providers/tools/server_mcp/`):
- `mcp_manager.py` - Manages multiple server-side MCP services with retry mechanisms
- `mcp_client.py` - Implements MCP client with stdio and SSE connection modes
- `mcp_executor.py` - Executes server-side MCP tools through the unified interface

**Device-side MCP Implementation** (`core/providers/tools/device_mcp/`):
- `mcp_client.py` - Manages MCP tool states and WebSocket communication for ESP32 devices
- `mcp_handler.py` - Processes MCP protocol messages and manages communication flow
- `mcp_executor.py` - Handles tool execution requests to ESP32 devices

**MCP Endpoint Implementation** (`core/providers/tools/mcp_endpoint/`):
- `mcp_endpoint_client.py` - WebSocket-based MCP client for external services
- `mcp_endpoint_handler.py` - Manages WebSocket connections and message processing
- `mcp_endpoint_executor.py` - Executes endpoint tools with response processing

##### Configuration System

**MCP Server Configuration** (`mcp_server_settings.json`):
```json
{
  "mcpServers": {
    "Home Assistant": {
      "command": "mcp-proxy",
      "args": ["http://YOUR_HA_HOST/mcp_server/sse"],
      "env": {"API_ACCESS_TOKEN": "YOUR_API_ACCESS_TOKEN"}
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"]
    }
  }
}
```

**Connection Modes**:
- **stdio**: Direct process communication with command-line MCP servers
- **SSE**: Server-Sent Events for HTTP-based MCP services

##### Tool Management and Execution

**Unified Tool Handler Architecture**:
The `UnifiedToolHandler` class coordinates all MCP executors through a centralized `ToolManager`:

```python
# Tool executor registration
self.tool_manager.register_executor(ToolType.SERVER_MCP, self.server_mcp_executor)
self.tool_manager.register_executor(ToolType.DEVICE_MCP, self.device_mcp_executor)
self.tool_manager.register_executor(ToolType.MCP_ENDPOINT, self.mcp_endpoint_executor)
```

**Tool Discovery Process**:
1. MCP clients establish connections to configured services
2. Tools are discovered through MCP protocol `list_tools` requests
3. Tool names are sanitized and mapped for consistent access
4. Function definitions are generated for LLM integration
5. Tools are registered with the unified tool manager

**Tool Execution Flow**:
1. LLM generates function call with tool name and parameters
2. Unified tool handler routes call to appropriate MCP executor
3. Executor invokes tool through respective MCP client
4. Results are processed and returned to the conversation flow
5. Error handling includes retry mechanisms and reconnection logic

##### Connection Management

**Server-side MCP Client Features**:
- Automatic process spawning for stdio-based MCP servers
- Environment variable injection for service configuration
- Connection health monitoring and automatic reconnection
- Tool name sanitization and mapping for consistent access
- Concurrent tool execution with proper resource isolation

**Device-side MCP Client Features**:
- WebSocket-based communication with ESP32 devices
- Async tool registration and state management
- Future-based result handling for tool execution
- Connection lifecycle management and cleanup
- Cached tool definitions for performance optimization

**MCP Endpoint Client Features**:
- WebSocket connection to external MCP endpoint services
- JWT authentication support for vision services
- Bidirectional message processing and tool execution
- Connection state management and error recovery
- Integration with management API for tool discovery

##### Error Handling and Resilience

**Retry Mechanisms**:
- Server MCP tools support up to 3 retry attempts with exponential backoff
- Automatic client reconnection on connection failures
- Graceful degradation when MCP services are unavailable
- Comprehensive logging for debugging connection issues

**Resource Management**:
- Proper cleanup of MCP client connections on shutdown
- Timeout handling for tool execution (configurable)
- Memory-efficient tool caching and state management
- Connection pooling for multiple concurrent tool calls

##### Integration with AI Pipeline

**Function Calling Integration**:
- MCP tools are exposed as standard function definitions to LLMs
- Seamless integration with existing function calling mechanisms
- Support for both single and batch tool execution
- Response processing through ActionResponse framework

**Multi-modal Capabilities**:
- Vision service integration through MCP endpoint architecture
- Image processing with JWT authentication
- Real-time tool execution during voice conversations
- Integration with device IoT capabilities for comprehensive automation

##### Management API Integration

**REST API Endpoints** (`main/manager-api/src/main/java/xiaozhi/modules/agent/controller/`):
- `AgentMcpAccessPointController.java` - Provides MCP access point management
- Tool list retrieval and permission validation
- MCP address generation for agent integration
- JSON-RPC request/response handling

**Service Layer** (`AgentMcpAccessPointServiceImpl.java`):
- MCP service discovery and tool enumeration
- Access control and permission management
- Integration with agent configuration system

This comprehensive MCP implementation enables the XiaoZhi ESP32 Server to serve as a powerful hub for external tool integration, supporting everything from home automation and file system operations to web automation and custom service integration, all while maintaining high performance and reliability for real-time voice assistant applications.

## Database Schema and Models

### Core Entities

**Device Management**:
- `tb_device` - Device registration and configuration
- `tb_ota` - OTA update information
- Fields: MAC address, board type, firmware version, agent binding

**Agent Management**:
- `tb_agent` - AI agent configurations
- `tb_agent_template` - Agent behavior templates
- `tb_agent_chat_history` - Conversation history
- `tb_agent_chat_audio` - Audio conversation records

**System Management**:
- `tb_sys_user` - User accounts and authentication
- `tb_sys_params` - System configuration parameters
- `tb_model_config` - AI model configurations
- `tb_model_provider` - Model provider settings

## Configuration Management

### Hierarchical Configuration

1. **Base Configuration**: `config.yaml` (default settings)
2. **Override Configuration**: `data/.config.yaml` (user customizations)
3. **API Configuration**: Dynamic settings from management API
4. **Device-specific Configuration**: Per-device model selection

### Key Configuration Sections

**Server Settings**:
```yaml
server:
  ip: 0.0.0.0
  port: 8000
  http_port: 8003
  websocket: ws://your-ip:port/xiaozhi/v1/
  auth:
    enabled: false
    tokens: [...]
```

**AI Model Configuration**:
```yaml
LLM:
  ChatGLMLLM:
    type: openai
    model_name: glm-4-flash
    api_key: your-api-key
    url: https://open.bigmodel.cn/api/paas/v4/
```

## API Reference

### REST API Endpoints

**Device Management**:
- `POST /device/register` - Register new device
- `POST /device/bind/{agentId}/{deviceCode}` - Bind device to agent
- `GET /device/bind/{agentId}` - Get bound devices
- `POST /device/unbind` - Unbind device

**Agent Management**:
- `GET /agent/list` - Get user agents
- `POST /agent` - Create agent
- `PUT /agent/{id}` - Update agent
- `DELETE /agent/{id}` - Delete agent

**Model Configuration**:
- `GET /models/list` - Get model configurations
- `POST /models/{modelType}/{provideCode}` - Add model
- `PUT /models/enable/{id}/{status}` - Enable/disable model

**OTA Management**:
- `POST /ota/` - Check updates and device status
- `GET /ota/` - Get OTA interface status

### WebSocket Protocol

**Message Types**:
- `hello` - Initial handshake and capability exchange
- `abort` - Interrupt current processing
- `listen` - Voice activity control
- `iot` - IoT device commands
- `mcp` - Model Context Protocol messages
- `server` - Administrative commands

**Audio Messages**:
- Binary WebSocket messages contain Opus-encoded audio
- 60ms frame duration for optimal latency
- Real-time bidirectional audio streaming

## Development and Deployment

### Local Development

**Python Server**:
```bash
cd main/xiaozhi-server
pip install -r requirements.txt
python app.py
```

**Java API**:
```bash
cd main/manager-api
mvn spring-boot:run
```

**Vue.js Web**:
```bash
cd main/manager-web
npm install
npm run serve
```

### Docker Deployment

**Simplified Deployment** (Server only):
- Docker image with Python server
- Configuration via environment variables
- Minimal resource requirements (2 core, 2GB RAM)

**Full Deployment** (All components):
- Multi-container setup with Docker Compose
- MySQL and Redis integration
- Web management interface
- Higher resource requirements (4 core, 8GB RAM)

### Configuration Options

**Free Configuration** (No API costs):
- FunASR (local ASR)
- ChatGLM (free LLM)
- EdgeTTS (free TTS)
- Local memory management

**Production Configuration** (Enhanced performance):
- DoubaoStreamASR (streaming ASR)
- Doubao LLM (enhanced language model)
- HuoshanDoubleStreamTTS (streaming TTS)
- External memory services

## Testing Tools

### Performance Testing

- `performance_tester.py` - Test ASR, LLM, TTS response times
- `performance_tester_vllm.py` - Test vision model performance
- `test/test_page.html` - Browser-based audio testing

### Audio Testing

- WebSocket audio streaming test
- Opus encoding/decoding verification
- Real-time latency measurement

## Extension Points

### Adding New AI Providers

1. Implement provider base class (ASR, LLM, TTS, VLLM)
2. Add configuration section in `config.yaml`
3. Register provider in module initialization
4. Test with performance testing tools

### Custom Plugin Development

1. Create function in `plugins_func/functions/`
2. Implement required interface methods
3. Add to configuration function list
4. Register with intent recognition system

### MCP Integration

1. Implement MCP client or server
2. Configure endpoint in `mcp_server_settings.json`
3. Register tools and resources
4. Test tool discovery and execution

## Security Considerations

### Authentication and Authorization

- JWT-based API authentication
- Device MAC address validation
- Optional Bearer token authentication
- Role-based access control

### Network Security

- CORS protection for web interfaces
- SQL injection prevention
- XSS filtering for user inputs
- Secure OTA download URLs

### Data Privacy

- Local AI processing options
- Encrypted communication channels
- User data isolation
- Configurable memory retention

## Performance Optimization

### ESP32 Optimization

- Opus audio compression (75% bandwidth reduction)
- 60ms frame timing for memory efficiency
- Connection pooling and resource management
- Power-aware connection timeouts

### Server Optimization

- Async/await architecture for concurrency
- Queue-based audio processing
- Connection isolation for scalability
- Streaming TTS for reduced latency

### Memory Management

- Per-connection resource isolation
- Automatic cleanup on disconnection
- Configurable memory limits
- Efficient audio buffer management

## Troubleshooting

### Common Issues

**Connection Problems**:
- Check WebSocket URL configuration
- Verify device authentication settings
- Confirm network connectivity

**Audio Issues**:
- Validate Opus codec support
- Check audio format compatibility
- Monitor audio queue status

**AI Service Problems**:
- Verify API keys and credentials
- Check model availability and quotas
- Monitor service response times

### Debugging Tools

- Comprehensive logging with configurable levels
- WebSocket connection monitoring
- Audio pipeline debugging
- Performance metrics collection

## Roadmap and Future Enhancements

### Planned Features

- Enhanced multi-modal interactions
- Advanced plugin ecosystem
- Edge AI acceleration support
- Cloud deployment templates

### Community Contributions

- Open source development model
- Community plugin marketplace
- Hardware partnership program
- Educational resources and tutorials

---

## Quick Reference

### Key File Locations

- **Main Server**: `main/xiaozhi-server/app.py`
- **Configuration**: `main/xiaozhi-server/config.yaml`
- **WebSocket Handler**: `main/xiaozhi-server/core/websocket_server.py`
- **Device Management**: `main/manager-api/src/main/java/xiaozhi/modules/device/`
- **Web Interface**: `main/manager-web/src/`

### Important Commands

```bash
# Run Python server
python main/xiaozhi-server/app.py

# Run Java API
cd main/manager-api && mvn spring-boot:run

# Run web interface
cd main/manager-web && npm run serve

# Performance testing
python main/xiaozhi-server/performance_tester.py
```

### Configuration Examples

```yaml
# Enable authentication
server:
  auth:
    enabled: true
    tokens:
      - token: "your-device-token"
        name: "device-name"

# Configure ChatGLM (free)
LLM:
  ChatGLMLLM:
    api_key: "your-chatglm-key"
    model_name: "glm-4-flash"
```

This comprehensive documentation provides a complete understanding of the XiaoZhi ESP32 Server project architecture, capabilities, and development practices.