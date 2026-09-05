from typing import Optional, Dict, Any
import struct
import random
from ..packets.builder import PacketBuilder
from ..packets.packet import PacketLayer
from ..common.utils import calculate_checksum, generate_ipv4


class IPv4Layer(PacketLayer):
    """IPv4 layer."""
    
    def __init__(
        self,
        src_ip: str,
        dst_ip: str,
        ttl: int = 64,
        protocol: int = 6,  # TCP
        data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name="ipv4",
            data={
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "ttl": ttl,
                "protocol": protocol,
                **(data or {}),
            }
        )
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ttl = ttl
        self.protocol = protocol
        self.build_raw()
    
    def build_raw(self, payload_length: int = 0) -> bytes:
        """Build IPv4 header."""
        # Convert IPs to bytes
        src_bytes = bytes(map(int, self.src_ip.split('.')))
        dst_bytes = bytes(map(int, self.dst_ip.split('.')))
        
        # Header fields
        version_ihl = 0x45  # Version 4, IHL 5 (20 bytes)
        tos = 0
        total_length = 20 + payload_length
        identification = random.randint(0, 65535)
        flags_fragment = 0x4000  # Don't fragment
        ttl = self.ttl
        protocol = self.protocol
        header_checksum = 0  # Will calculate later
        
        # Build header without checksum
        header = struct.pack(
            "!BBHHHBBHII",
            version_ihl,
            tos,
            total_length,
            identification,
            flags_fragment,
            ttl,
            protocol,
            header_checksum,
            int.from_bytes(src_bytes, 'big'),
            int.from_bytes(dst_bytes, 'big'),
        )
        
        # Calculate checksum
        checksum = calculate_checksum(header)
        # Rebuild with checksum
        header = struct.pack(
            "!BBHHHBBHII",
            version_ihl,
            tos,
            total_length,
            identification,
            flags_fragment,
            ttl,
            protocol,
            checksum,
            int.from_bytes(src_bytes, 'big'),
            int.from_bytes(dst_bytes, 'big'),
        )
        
        self.raw = header
        self.data["raw"] = header
        return header


class IPv4Builder(PacketBuilder):
    """IPv4 packet builder."""
    
    def __init__(self):
        super().__init__()
        self.packet.add_layer(
            PacketLayer(
                name="ipv4",
                data={"builder": "IPv4Builder"}
            )
        )
    
    def build_header(
        self,
        src: Optional[str] = None,
        dst: Optional[str] = None,
        ttl: int = 64,
        protocol: int = 6,
        **kwargs
    ) -> bytes:
        """Build IPv4 header."""
        src = src or generate_ipv4()
        dst = dst or generate_ipv4()
        
        # Parse IPs
        src_bytes = bytes(map(int, src.split('.')))
        dst_bytes = bytes(map(int, dst.split('.')))
        
        # Header (without payload length initially)
        version_ihl = 0x45
        tos = 0
        total_length = 20  # Will be updated later
        identification = random.randint(0, 65535)
        flags_fragment = 0x4000
        header_checksum = 0
        
        header = struct.pack(
            "!BBHHHBBHII",
            version_ihl,
            tos,
            total_length,
            identification,
            flags_fragment,
            ttl,
            protocol,
            header_checksum,
            int.from_bytes(src_bytes, 'big'),
            int.from_bytes(dst_bytes, 'big'),
        )
        
        # Store layer data
        layer_data = {
            "src": src,
            "dst": dst,
            "ttl": ttl,
            "protocol": protocol,
        }
        self.add_layer("ipv4", layer_data, header)
        
        return header
    
    def build_payload(self, payload: bytes) -> bytes:
        """Build with payload."""
        # Update total length
        if self.packet.get_layer("ipv4"):
            layer = self.packet.get_layer("ipv4")
            if layer and layer.raw:
                old_header = layer.raw
                # Update total length
                total_length = 20 + len(payload)
                new_header = old_header[:2] + struct.pack("!H", total_length) + old_header[4:]
                # Recalculate checksum
                checksum = calculate_checksum(new_header)
                new_header = new_header[:10] + struct.pack("!H", checksum) + new_header[12:]
                layer.raw = new_header
        
        return payload
