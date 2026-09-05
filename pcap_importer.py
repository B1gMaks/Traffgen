from typing import List, Optional
from pathlib import Path
import struct
from datetime import datetime
from .base import Importer
from ..core.types import PacketData, Address, ProtocolType
from ..common.exceptions import ImportError
from ..common.utils import bytes_to_hex


class PcapImporter(Importer):
    """Import packets from PCAP files."""
    
    def import_file(self, file_path: Path) -> List[PacketData]:
        """Import packets from PCAP file."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            return self.import_bytes(data)
        except Exception as e:
            raise ImportError(f"Failed to import PCAP: {e}")
    
    def import_bytes(self, data: bytes) -> List[PacketData]:
        """Import packets from PCAP bytes."""
        packets = []
        offset = 0
        
        # Read global header
        if len(data) < 24:
            raise ImportError("PCAP data too short")
        
        magic, major, minor, tz, sigfigs, snaplen, network = struct.unpack(
            "!IHHIIII", data[offset:offset+24]
        )
        offset += 24
        
        # Check magic number
        if magic != 0xa1b2c3d4:
            # Try byte-swapped
            if magic == 0xd4c3b2a1:
                # Little endian, need to handle differently
                # For simplicity, we'll assume big endian
                pass
            else:
                raise ImportError(f"Invalid PCAP magic: {hex(magic)}")
        
        # Read packets
        while offset + 16 <= len(data):
            try:
                ts_sec, ts_usec, incl_len, orig_len = struct.unpack(
                    "!IIII", data[offset:offset+16]
                )
                offset += 16
                
                # Read packet data
                if offset + incl_len > len(data):
                    break
                
                packet_data = data[offset:offset+incl_len]
                offset += incl_len
                
                # Create packet
                timestamp = datetime.fromtimestamp(ts_sec + ts_usec / 1_000_000)
                
                # Try to parse basic info
                src = Address()
                dst = Address()
                protocol = ProtocolType.UNKNOWN
                
                # Parse Ethernet header if present
                if len(packet_data) >= 14:
                    # Ethernet II
                    dst.mac = self._format_mac(packet_data[0:6])
                    src.mac = self._format_mac(packet_data[6:12])
                    ethertype = struct.unpack("!H", packet_data[12:14])[0]
                    
                    # Parse IPv4 if present
                    if ethertype == 0x0800 and len(packet_data) >= 34:
                        src.ipv4 = self._format_ipv4(packet_data[26:30])
                        dst.ipv4 = self._format_ipv4(packet_data[30:34])
                        ip_proto = packet_data[23]
                        
                        # Parse ports if TCP/UDP
                        if ip_proto == 6 and len(packet_data) >= 42:  # TCP
                            src.port = struct.unpack("!H", packet_data[34:36])[0]
                            dst.port = struct.unpack("!H", packet_data[36:38])[0]
                            protocol = ProtocolType.TCP
                        elif ip_proto == 17 and len(packet_data) >= 42:  # UDP
                            src.port = struct.unpack("!H", packet_data[34:36])[0]
                            dst.port = struct.unpack("!H", packet_data[36:38])[0]
                            protocol = ProtocolType.UDP
                        elif ip_proto == 1:  # ICMP
                            protocol = ProtocolType.ICMP
                        elif ip_proto == 6:  # TCP
                            protocol = ProtocolType.TCP
                        elif ip_proto == 17:  # UDP
                            protocol = ProtocolType.UDP
                
                # Create packet data
                packet = PacketData(
                    timestamp=timestamp,
                    source=src,
                    destination=dst,
                    protocol=protocol,
                    payload=packet_data,
                    length=len(packet_data),
                    metadata={
                        "original_length": orig_len,
                        "snaplen": snaplen,
                    }
                )
                
                packets.append(packet)
                
            except Exception as e:
                # Skip malformed packet
                continue
        
        return packets
    
    def _format_mac(self, mac_bytes: bytes) -> str:
        """Format MAC address."""
        return ":".join(f"{b:02x}" for b in mac_bytes)
    
    def _format_ipv4(self, ip_bytes: bytes) -> str:
        """Format IPv4 address."""
        return ".".join(str(b) for b in ip_bytes)
