from typing import List, Dict, Any
from pathlib import Path
import csv
from .base import Exporter
from ..core.types import PacketData
from ..common.exceptions import ExportError


class CSVExporter(Exporter):
    """Export packets to CSV format."""
    
    def export(self, packets: List[PacketData], output_path: Path, **kwargs) -> None:
        """Export packets to CSV file."""
        try:
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'timestamp', 'src_mac', 'dst_mac', 'src_ip', 'dst_ip',
                    'src_port', 'dst_port', 'protocol', 'length'
                ])
                
                # Write data
                for packet in packets:
                    writer.writerow([
                        packet.timestamp.isoformat(),
                        packet.source.mac or '',
                        packet.destination.mac or '',
                        packet.source.ipv4 or '',
                        packet.destination.ipv4 or '',
                        packet.source.port or '',
                        packet.destination.port or '',
                        packet.protocol.value,
                        packet.length,
                    ])
        except Exception as e:
            raise ExportError(f"Failed to export CSV: {e}")
    
    def export_string(self, packets: List[PacketData], **kwargs) -> str:
        """Export packets as CSV string."""
        import io
        output = io.StringIO()
        
        writer = csv.writer(output)
        writer.writerow([
            'timestamp', 'src_mac', 'dst_mac', 'src_ip', 'dst_ip',
            'src_port', 'dst_port', 'protocol', 'length'
        ])
        
        for packet in packets:
            writer.writerow([
                packet.timestamp.isoformat(),
                packet.source.mac or '',
                packet.destination.mac or '',
                packet.source.ipv4 or '',
                packet.destination.ipv4 or '',
                packet.source.port or '',
                packet.destination.port or '',
                packet.protocol.value,
                packet.length,
            ])
        
        return output.getvalue()
