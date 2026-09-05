from typing import List, Optional
from pathlib import Path
import struct
import time
from datetime import datetime
from .base import Exporter
from ..core.types import PacketData
from ..common.exceptions import ExportError


class PcapExporter(Exporter):
    """Export packets to PCAP format."""
    
    # PCAP global header
    PCAP_MAGIC = 0xa1b2c3d4
    PCAP_VERSION_MAJOR = 2
    PCAP_VERSION_MINOR = 4
    PCAP_THISZONE = 0
    PCAP_SIGFIGS = 0
    PCAP_SNAPLEN = 65535
    PCAP_NETWORK = 1  # Ethernet
    
    def export(self, packets: List[PacketData], output_path: Path, **kwargs) -> None:
        """Export packets to PCAP file."""
        try:
            with open(output_path, 'wb') as f:
                # Write global header
                f.write(self._build_global_header())
                
                # Write each packet
                for packet in packets:
                    f.write(self._build_packet_header(packet))
                    f.write(packet.payload)
        except Exception as e:
            raise ExportError(f"Failed to export PCAP: {e}")
    
    def export_string(self, packets: List[PacketData], **kwargs) -> str:
        """Export packets as PCAP bytes (hex string)."""
        data = bytearray()
        data.extend(self._build_global_header())
        
        for packet in packets:
            data.extend(self._build_packet_header(packet))
            data.extend(packet.payload)
        
        return data.hex()
    
    def _build_global_header(self) -> bytes:
        """Build PCAP global header."""
        return struct.pack(
            "!IHHIIII",
            self.PCAP_MAGIC,
            self.PCAP_VERSION_MAJOR,
            self.PCAP_VERSION_MINOR,
            self.PCAP_THISZONE,
            self.PCAP_SIGFIGS,
            self.PCAP_SNAPLEN,
            self.PCAP_NETWORK,
        )
    
    def _build_packet_header(self, packet: PacketData) -> bytes:
        """Build PCAP packet header."""
        # Convert timestamp to seconds and microseconds
        ts = packet.timestamp.timestamp()
        ts_sec = int(ts)
        ts_usec = int((ts - ts_sec) * 1_000_000)
        
        # Packet length (actual data)
        incl_len = len(packet.payload)
        orig_len = incl_len
        
        return struct.pack(
            "!IIII",
            ts_sec,
            ts_usec,
            incl_len,
            orig_len,
        )
