"""Device Trigger Handler - API for triggering device responses remotely"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from aiohttp import web
from config.logger import setup_logging
from core.utils.util import filter_sensitive_info

TAG = __name__


class DeviceTriggerHandler:
    """Handler for device trigger API endpoints"""

    def __init__(self, config: dict, websocket_server=None):
        self.config = config
        self.websocket_server = websocket_server
        self.logger = setup_logging()
        self.auth_key = config.get("server", {}).get("auth_key", "")

    def set_websocket_server(self, websocket_server):
        """Set the WebSocket server instance to access active connections"""
        self.websocket_server = websocket_server

    def _authenticate_request(self, request) -> bool:
        """Authenticate API requests using auth key"""
        if not self.auth_key:
            return True  # No auth required if no key set
        
        # Check Authorization header
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            return token == self.auth_key
        
        # Check query parameter
        auth_param = request.query.get('auth_key', '')
        return auth_param == self.auth_key

    def _get_device_connection(self, device_id: str):
        """Get device connection by device ID"""
        if not self.websocket_server:
            return None
        
        for connection in self.websocket_server.active_connections:
            if connection.device_id == device_id:
                return connection
        return None

    def _get_all_device_connections(self):
        """Get all active device connections"""
        if not self.websocket_server:
            self.logger.bind(tag=TAG).warning("WebSocket server not available")
            return []
        
        connections = list(self.websocket_server.active_connections)
        self.logger.bind(tag=TAG).debug(f"Found {len(connections)} active connections")
        return connections

    def _add_cors_headers(self, response):
        """Add CORS headers to response"""
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400'
        })
        return response

    def _json_response(self, data, status=200):
        """Create JSON response with CORS headers"""
        response = web.json_response(data, status=status)
        return self._add_cors_headers(response)

    async def handle_options(self, request):
        """Handle CORS preflight requests"""
        response = web.Response()
        return self._add_cors_headers(response)

    async def list_devices(self, request):
        """List all connected devices"""
        try:
            # Authentication check
            if not self._authenticate_request(request):
                return self._json_response(
                    {"error": "Unauthorized", "message": "Invalid auth key"}, 
                    status=401
                )

            connections = self._get_all_device_connections()
            devices = []
            
            for conn in connections:
                device_info = {
                    "device_id": conn.device_id,
                    "client_ip": conn.client_ip,
                    "session_id": conn.session_id,
                    "connected_at": conn.last_activity_time,
                    "is_speaking": conn.client_is_speaking,
                    "listen_mode": conn.client_listen_mode,
                    "audio_format": conn.audio_format,
                    "features": conn.features,
                    "client_info": filter_sensitive_info(conn.headers) if conn.headers else {}
                }
                devices.append(device_info)

            response_data = {
                "status": "success",
                "devices": devices,
                "total_count": len(devices)
            }
            
            self.logger.bind(tag=TAG).info(f"Listed {len(devices)} connected devices")
            return self._json_response(response_data)

        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Error listing devices: {str(e)}")
            return self._json_response(
                {"error": "Internal Server Error", "message": str(e)}, 
                status=500
            )

    async def trigger_device_message(self, request):
        """Trigger a message/response on a specific device"""
        try:
            # Authentication check
            if not self._authenticate_request(request):
                return self._json_response(
                    {"error": "Unauthorized", "message": "Invalid auth key"}, 
                    status=401
                )

            device_id = request.match_info.get('device_id')
            if not device_id:
                return self._json_response(
                    {"error": "Bad Request", "message": "Device ID is required"}, 
                    status=400
                )

            # Parse request body
            try:
                body = await request.json()
            except Exception:
                return self._json_response(
                    {"error": "Bad Request", "message": "Invalid JSON body"}, 
                    status=400
                )

            message = body.get('message', '')
            message_type = body.get('type', 'chat')  # chat, tts, function_call
            close_after = body.get('close_after', False)

            if not message:
                return self._json_response(
                    {"error": "Bad Request", "message": "Message is required"}, 
                    status=400
                )

            # Find device connection
            connection = self._get_device_connection(device_id)
            if not connection:
                return self._json_response(
                    {"error": "Not Found", "message": f"Device {device_id} not connected"}, 
                    status=404
                )

            # Execute the trigger based on type
            if message_type == 'chat':
                # Trigger a chat response
                if close_after:
                    connection.chat_and_close(message)
                else:
                    connection.chat(message)
                    
            elif message_type == 'tts':
                # Direct TTS output
                if connection.tts:
                    from core.providers.tts.dto.dto import ContentType
                    connection.tts.tts_one_sentence(connection, ContentType.TEXT, content_detail=message)
                    
            elif message_type == 'function_call':
                # Execute a function call
                function_name = body.get('function_name')
                function_args = body.get('function_args', {})
                
                if not function_name:
                    return self._json_response(
                        {"error": "Bad Request", "message": "Function name is required for function_call type"}, 
                        status=400
                    )
                
                if hasattr(connection, 'func_handler') and connection.func_handler:
                    function_call_data = {
                        "name": function_name,
                        "id": f"trigger_{device_id}_{asyncio.get_event_loop().time()}",
                        "arguments": json.dumps(function_args)
                    }
                    
                    result = await connection.func_handler.handle_llm_function_call(
                        connection, function_call_data
                    )
                    connection._handle_function_result(result, function_call_data)
                else:
                    return self._json_response(
                        {"error": "Service Unavailable", "message": "Function handler not available"}, 
                        status=503
                    )
            else:
                return self._json_response(
                    {"error": "Bad Request", "message": f"Invalid message type: {message_type}"}, 
                    status=400
                )

            response_data = {
                "status": "success",
                "message": f"Message triggered on device {device_id}",
                "device_id": device_id,
                "triggered_type": message_type,
                "session_id": connection.session_id
            }
            
            self.logger.bind(tag=TAG).info(f"Triggered {message_type} message on device {device_id}: {message[:50]}...")
            return self._json_response(response_data)

        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Error triggering device message: {str(e)}")
            return self._json_response(
                {"error": "Internal Server Error", "message": str(e)}, 
                status=500
            )

    async def broadcast_message(self, request):
        """Broadcast a message to all connected devices"""
        try:
            # Authentication check
            if not self._authenticate_request(request):
                return self._json_response(
                    {"error": "Unauthorized", "message": "Invalid auth key"}, 
                    status=401
                )

            # Parse request body
            try:
                body = await request.json()
            except Exception:
                return self._json_response(
                    {"error": "Bad Request", "message": "Invalid JSON body"}, 
                    status=400
                )

            message = body.get('message', '')
            message_type = body.get('type', 'chat')
            device_filter = body.get('device_filter', {})  # Optional device filtering
            close_after = body.get('close_after', False)

            if not message:
                return self._json_response(
                    {"error": "Bad Request", "message": "Message is required"}, 
                    status=400
                )

            connections = self._get_all_device_connections()
            if not connections:
                return self._json_response(
                    {"error": "Not Found", "message": "No devices connected"}, 
                    status=404
                )

            # Filter connections if device_filter is provided
            if device_filter:
                filtered_connections = []
                for conn in connections:
                    match = True
                    if 'device_ids' in device_filter:
                        match = match and conn.device_id in device_filter['device_ids']
                    if 'client_ips' in device_filter:
                        match = match and conn.client_ip in device_filter['client_ips']
                    if match:
                        filtered_connections.append(conn)
                connections = filtered_connections

            # Broadcast to all matching connections
            triggered_devices = []
            for connection in connections:
                try:
                    if message_type == 'chat':
                        if close_after:
                            connection.chat_and_close(message)
                        else:
                            connection.chat(message)
                    elif message_type == 'tts':
                        if connection.tts:
                            from core.providers.tts.dto.dto import ContentType
                            connection.tts.tts_one_sentence(connection, ContentType.TEXT, content_detail=message)
                    
                    triggered_devices.append({
                        "device_id": connection.device_id,
                        "session_id": connection.session_id,
                        "status": "triggered"
                    })
                except Exception as e:
                    triggered_devices.append({
                        "device_id": connection.device_id,
                        "session_id": connection.session_id,
                        "status": "error",
                        "error": str(e)
                    })

            response_data = {
                "status": "success",
                "message": f"Message broadcast to {len(triggered_devices)} devices",
                "triggered_devices": triggered_devices,
                "broadcast_type": message_type
            }
            
            self.logger.bind(tag=TAG).info(f"Broadcast {message_type} message to {len(triggered_devices)} devices: {message[:50]}...")
            return self._json_response(response_data)

        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Error broadcasting message: {str(e)}")
            return self._json_response(
                {"error": "Internal Server Error", "message": str(e)}, 
                status=500
            )

    async def get_device_status(self, request):
        """Get detailed status of a specific device"""
        try:
            # Authentication check
            if not self._authenticate_request(request):
                return self._json_response(
                    {"error": "Unauthorized", "message": "Invalid auth key"}, 
                    status=401
                )

            device_id = request.match_info.get('device_id')
            if not device_id:
                return self._json_response(
                    {"error": "Bad Request", "message": "Device ID is required"}, 
                    status=400
                )

            connection = self._get_device_connection(device_id)
            if not connection:
                return self._json_response(
                    {"error": "Not Found", "message": f"Device {device_id} not connected"}, 
                    status=404
                )

            # Get available functions
            available_functions = []
            if hasattr(connection, 'func_handler') and connection.func_handler:
                functions = connection.func_handler.get_functions()
                for func_name, func_def in functions.items():
                    available_functions.append({
                        "name": func_name,
                        "description": func_def.get('description', ''),
                        "parameters": func_def.get('parameters', {})
                    })

            device_status = {
                "device_id": connection.device_id,
                "session_id": connection.session_id,
                "client_ip": connection.client_ip,
                "connected_at": connection.last_activity_time,
                "is_speaking": connection.client_is_speaking,
                "listen_mode": connection.client_listen_mode,
                "audio_format": connection.audio_format,
                "features": connection.features,
                "llm_busy": not connection.llm_finish_task,
                "close_after_chat": connection.close_after_chat,
                "intent_type": connection.intent_type,
                "available_functions": available_functions,
                "client_info": filter_sensitive_info(connection.headers) if connection.headers else {},
                "config_summary": {
                    "prompt_set": bool(connection.prompt),
                    "memory_enabled": bool(connection.memory),
                    "tts_enabled": bool(connection.tts),
                    "asr_enabled": bool(connection.asr),
                    "vad_enabled": bool(connection.vad)
                }
            }

            self.logger.bind(tag=TAG).info(f"Retrieved status for device {device_id}")
            return self._json_response({"status": "success", "device": device_status})

        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Error getting device status: {str(e)}")
            return self._json_response(
                {"error": "Internal Server Error", "message": str(e)}, 
                status=500
            )

    async def disconnect_device(self, request):
        """Disconnect a specific device"""
        try:
            # Authentication check
            if not self._authenticate_request(request):
                return self._json_response(
                    {"error": "Unauthorized", "message": "Invalid auth key"}, 
                    status=401
                )

            device_id = request.match_info.get('device_id')
            if not device_id:
                return self._json_response(
                    {"error": "Bad Request", "message": "Device ID is required"}, 
                    status=400
                )

            connection = self._get_device_connection(device_id)
            if not connection:
                return self._json_response(
                    {"error": "Not Found", "message": f"Device {device_id} not connected"}, 
                    status=404
                )

            # Close the connection
            await connection.close()

            response_data = {
                "status": "success",
                "message": f"Device {device_id} disconnected",
                "device_id": device_id
            }
            
            self.logger.bind(tag=TAG).info(f"Disconnected device {device_id}")
            return self._json_response(response_data)

        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Error disconnecting device: {str(e)}")
            return self._json_response(
                {"error": "Internal Server Error", "message": str(e)}, 
                status=500
            )