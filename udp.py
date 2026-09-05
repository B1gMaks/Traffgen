from typing import Optional, Dict, Any
import struct
from ..packets.builder import PacketBuilder
from ..packets.packet import PacketLayer
from ..common.utils import generate_port
from ..common.validators import validate_port


class UDPLayer(PacketLayer):
    """UDP layer."""
    
    def __init__(
        self,
        src_port: int,
        dst_port: int,
        data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name="udp",
            data={
                "src_port": src_port,
                "dst_port": dst_port,
                **(data or {}),
            }
        )
        self.src_port = src_port
        self.dst_port = dst_port
        self.build_raw()
    
    def build_raw(self, payload_length: int = 0) -> bytes:
        """Build UDP header."""
        # Header fields
        length = 8 + payload_length
        checksum = 0
        
        header = struct.pack(
            "!HHHH",
            self.src_port,
            self.dst_port,
            length,
            checksum,
        )
        
        self.raw = header
        self.data["raw"] = header
        self.data["length"] = length
        return header


class UDPBuilder(PacketBuilder):
    """UDP packet builder."""
    
    def __init__(self):
        super().__init__()
        self.packet.add_layer(
            PacketLayer(
                name="udp",
                data={"builder": "UDPBuilder"}
            )
        )
    
    def build_header(
        self,
        src_port: Optional[int] = None,
        dst_port: Optional[int] = None,
        **kwargs
    ) -> bytes:
        """Build UDP header."""
        src_port = src_port or generate_port()
        dst_port = dst_port or generate_port()
        
        # Validate ports
        if not validate_port(src_port) or not validate_port(dst_port):
            raise ValueError("Invalid port number")
        
        # Header (without payload length)
        length = 8  # Will be updated
        checksum = 0
        
        header = struct.pack(
            "!HHHH",
            src_port,
            dst_port,
            length,
            checksum,
        )
        
        # Store layer data
        layer_data = {
            "src_port": src_port,
            "dst_port": dst_port,
        }
        self.add_layer("udp", layer_data, header)
        
        return header
    
    def build_payload(self, payload: bytes) -> bytes:
        """Build with payload."""
        # Update UDP length
        if self.packet.get_layer("udp"):
            layer = self.packet.get_layer("udp")
            if layer and layer.raw:
                total_length = 8 + len(payload)
                # Update length in header
                new_header = layer.raw[:4] + struct.pack("!H", total_length) + layer.raw[6:]
                layer.raw = new_header
        
        return payload
