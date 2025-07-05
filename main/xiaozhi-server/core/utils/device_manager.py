"""Device Manager - Utilities for managing device connections and operations"""

import json
import time
from typing import Dict, List, Optional, Any
from config.logger import setup_logging

TAG = __name__


class DeviceManager:
    """Manager class for device operations and connection utilities"""

    def __init__(self, websocket_server=None):
        self.websocket_server = websocket_server
        self.logger = setup_logging()

    def set_websocket_server(self, websocket_server):
        """Set the WebSocket server instance"""
        self.websocket_server = websocket_server

    def get_all_devices(self) -> List[Dict[str, Any]]:
        """Get information about all connected devices"""
        if not self.websocket_server:
            return []

        devices = []
        for conn in self.websocket_server.active_connections:
            device_info = self._extract_device_info(conn)
            devices.append(device_info)

        return devices

    def get_device_by_id(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device information by device ID"""
        if not self.websocket_server:
            return None

        for conn in self.websocket_server.active_connections:
            if conn.device_id == device_id:
                return self._extract_device_info(conn)

        return None

    def get_device_connection(self, device_id: str):
        """Get device connection object by device ID"""
        if not self.websocket_server:
            return None

        for conn in self.websocket_server.active_connections:
            if conn.device_id == device_id:
                return conn

        return None

    def get_devices_by_filter(self, filter_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get devices filtered by criteria"""
        all_devices = self.get_all_devices()
        filtered_devices = []

        for device in all_devices:
            matches = True

            # Filter by device IDs
            if 'device_ids' in filter_criteria:
                matches = matches and device['device_id'] in filter_criteria['device_ids']

            # Filter by client IPs
            if 'client_ips' in filter_criteria:
                matches = matches and device['client_ip'] in filter_criteria['client_ips']

            # Filter by connection status
            if 'is_speaking' in filter_criteria:
                matches = matches and device['is_speaking'] == filter_criteria['is_speaking']

            # Filter by listen mode
            if 'listen_mode' in filter_criteria:
                matches = matches and device['listen_mode'] == filter_criteria['listen_mode']

            # Filter by features
            if 'has_mcp' in filter_criteria:
                has_mcp = device.get('features', {}).get('mcp', False) if device.get('features') else False
                matches = matches and has_mcp == filter_criteria['has_mcp']

            if matches:
                filtered_devices.append(device)

        return filtered_devices

    def _extract_device_info(self, connection) -> Dict[str, Any]:
        """Extract device information from connection object"""
        return {
            "device_id": connection.device_id,
            "session_id": connection.session_id,
            "client_ip": connection.client_ip,
            "connected_at": connection.last_activity_time,
            "connection_duration": time.time() * 1000 - connection.last_activity_time,
            "is_speaking": connection.client_is_speaking,
            "listen_mode": connection.client_listen_mode,
            "audio_format": connection.audio_format,
            "features": connection.features,
            "llm_busy": not connection.llm_finish_task,
            "close_after_chat": connection.close_after_chat,
            "intent_type": connection.intent_type,
            "has_voice": connection.client_have_voice,
            "voice_stopped": connection.client_voice_stop,
            "config_from_api": connection.read_config_from_api,
            "needs_binding": connection.need_bind,
            "bind_code": connection.bind_code if hasattr(connection, 'bind_code') else None,
            "client_info": {
                "user_agent": connection.headers.get("user-agent") if connection.headers else None,
                "client_version": connection.headers.get("client-version") if connection.headers else None,
                "board_type": connection.headers.get("board-type") if connection.headers else None,
                "firmware_version": connection.headers.get("firmware-version") if connection.headers else None
            }
        }

    def get_device_statistics(self) -> Dict[str, Any]:
        """Get overall device connection statistics"""
        devices = self.get_all_devices()
        
        stats = {
            "total_devices": len(devices),
            "speaking_devices": len([d for d in devices if d['is_speaking']]),
            "idle_devices": len([d for d in devices if not d['is_speaking']]),
            "auto_listen_devices": len([d for d in devices if d['listen_mode'] == 'auto']),
            "manual_listen_devices": len([d for d in devices if d['listen_mode'] == 'manual']),
            "mcp_enabled_devices": len([d for d in devices if d.get('features', {}).get('mcp', False)]),
            "api_config_devices": len([d for d in devices if d['config_from_api']]),
            "local_config_devices": len([d for d in devices if not d['config_from_api']]),
            "devices_needing_binding": len([d for d in devices if d['needs_binding']]),
            "average_connection_duration": sum([d['connection_duration'] for d in devices]) / len(devices) if devices else 0,
            "device_types": {}
        }

        # Count device types by board type
        for device in devices:
            board_type = device['client_info'].get('board_type', 'unknown')
            stats['device_types'][board_type] = stats['device_types'].get(board_type, 0) + 1

        return stats

    async def broadcast_to_devices(self, message: Dict[str, Any], device_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Broadcast a message to devices with optional filtering"""
        if not self.websocket_server:
            return []

        target_devices = self.get_devices_by_filter(device_filter) if device_filter else self.get_all_devices()
        results = []

        for device_info in target_devices:
            connection = self.get_device_connection(device_info['device_id'])
            if connection:
                try:
                    await connection.websocket.send(json.dumps(message))
                    results.append({
                        "device_id": device_info['device_id'],
                        "status": "sent",
                        "timestamp": time.time() * 1000
                    })
                    self.logger.bind(tag=TAG).debug(f"Broadcast message sent to device {device_info['device_id']}")
                except Exception as e:
                    results.append({
                        "device_id": device_info['device_id'],
                        "status": "error",
                        "error": str(e),
                        "timestamp": time.time() * 1000
                    })
                    self.logger.bind(tag=TAG).error(f"Failed to send broadcast to device {device_info['device_id']}: {str(e)}")

        return results

    async def disconnect_device(self, device_id: str) -> bool:
        """Disconnect a specific device"""
        connection = self.get_device_connection(device_id)
        if connection:
            try:
                await connection.close()
                self.logger.bind(tag=TAG).info(f"Disconnected device {device_id}")
                return True
            except Exception as e:
                self.logger.bind(tag=TAG).error(f"Failed to disconnect device {device_id}: {str(e)}")
                return False
        return False

    async def disconnect_devices_by_filter(self, filter_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Disconnect devices matching filter criteria"""
        target_devices = self.get_devices_by_filter(filter_criteria)
        results = []

        for device_info in target_devices:
            success = await self.disconnect_device(device_info['device_id'])
            results.append({
                "device_id": device_info['device_id'],
                "status": "disconnected" if success else "failed",
                "timestamp": time.time() * 1000
            })

        return results

    def get_device_functions(self, device_id: str) -> List[Dict[str, Any]]:
        """Get available functions for a specific device"""
        connection = self.get_device_connection(device_id)
        if not connection or not hasattr(connection, 'func_handler') or not connection.func_handler:
            return []

        functions = []
        try:
            func_definitions = connection.func_handler.get_functions()
            for func_name, func_def in func_definitions.items():
                functions.append({
                    "name": func_name,
                    "description": func_def.get('description', ''),
                    "parameters": func_def.get('parameters', {}),
                    "tool_type": func_def.get('tool_type', 'unknown')
                })
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Failed to get functions for device {device_id}: {str(e)}")

        return functions

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on device connections"""
        devices = self.get_all_devices()
        current_time = time.time() * 1000
        
        healthy_devices = []
        unhealthy_devices = []
        
        for device in devices:
            # Check if device is responsive (last activity within 5 minutes)
            time_since_activity = current_time - device['connected_at']
            is_healthy = time_since_activity < 300000  # 5 minutes in milliseconds
            
            device_health = {
                "device_id": device['device_id'],
                "is_healthy": is_healthy,
                "time_since_activity": time_since_activity,
                "connection_duration": device['connection_duration']
            }
            
            if is_healthy:
                healthy_devices.append(device_health)
            else:
                unhealthy_devices.append(device_health)

        return {
            "healthy_devices": healthy_devices,
            "unhealthy_devices": unhealthy_devices,
            "total_healthy": len(healthy_devices),
            "total_unhealthy": len(unhealthy_devices),
            "health_percentage": (len(healthy_devices) / len(devices) * 100) if devices else 100
        }