from typing import List, Dict, Any
from pathlib import Path
import json
from datetime import datetime
from .base import Exporter
from ..core.types import PacketData
from ..common.exceptions import ExportError


class JSONExporter(Exporter):
    """Export packets to JSON format."""
    
    def export(self, packets: List[PacketData], output_path: Path, **kwargs) -> None:
        """Export packets to JSON file."""
        try:
            data = self._build_json(packets, **kwargs)
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2, default=self._json_serializer)
        except Exception as e:
            raise ExportError(f"Failed to export JSON: {e}")
    
    def export_string(self, packets: List[PacketData], **kwargs) -> str:
        """Export packets as JSON string."""
        data = self._build_json(packets, **kwargs)
        return json.dumps(data, indent=2, default=self._json_serializer)
    
    def _build_json(self, packets: List[PacketData], **kwargs) -> Dict[str, Any]:
        """Build JSON structure."""
        return {
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "packet_count": len(packets),
                "format": "json",
                **self._metadata,
            },
            "packets": [self._packet_to_dict(p) for p in packets],
        }
    
    def _packet_to_dict(self, packet: PacketData) -> Dict[str, Any]:
        """Convert packet to dictionary."""
        return {
            "timestamp": packet.timestamp.isoformat(),
            "source": {
                "mac": packet.source.mac,
                "ipv4": packet.source.ipv4,
                "ipv6": packet.source.ipv6,
                "port": packet.source.port,
            },
            "destination": {
                "mac": packet.destination.mac,
                "ipv4": packet.destination.ipv4,
                "ipv6": packet.destination.ipv6,
                "port": packet.destination.port,
            },
            "protocol": packet.protocol.value,
            "length": packet.length,
            "payload": packet.payload.hex(),
            "layers": packet.layers,
        }
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
