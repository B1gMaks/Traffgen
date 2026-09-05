from typing import List, Dict, Any
from pathlib import Path
import yaml
from datetime import datetime
from .base import Exporter
from ..core.types import PacketData
from ..common.exceptions import ExportError


class YAMLExporter(Exporter):
    """Export packets to YAML format."""
    
    def export(self, packets: List[PacketData], output_path: Path, **kwargs) -> None:
        """Export packets to YAML file."""
        try:
            data = self._build_yaml(packets, **kwargs)
            with open(output_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            raise ExportError(f"Failed to export YAML: {e}")
    
    def export_string(self, packets: List[PacketData], **kwargs) -> str:
        """Export packets as YAML string."""
        data = self._build_yaml(packets, **kwargs)
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)
    
    def _build_yaml(self, packets: List[PacketData], **kwargs) -> Dict[str, Any]:
        """Build YAML structure."""
        return {
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "packet_count": len(packets),
                "format": "yaml",
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
