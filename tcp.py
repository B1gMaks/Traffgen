from typing import Optional, Dict, Any
import struct
import random
from ..packets.builder import PacketBuilder
from ..packets.packet import PacketLayer
from ..common.utils import calculate_checksum, generate_port
from ..common.validators import validate_port


class TCPLayer(PacketLayer):
    """TCP layer."""
    
    def __init__(
        self,
        src_port: int,
        dst_port: int,
        seq_num: Optional[int] = None,
        ack_num: int = 0,
        flags: int = 0x02,  # SYN by default
        window: int = 65535,
        data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name="tcp",
            data={
                "src_port": src_port,
                "dst_port": dst_port,
                "seq_num": seq_num or random.randint(0, 0xffffffff),
                "ack_num": ack_num,
                "flags": flags,
                "window": window,
                **(data or {}),
            }
        )
        self.src_port = src_port
        self.dst_port = dst_port
        self.seq_num = seq_num or random.randint(0, 0xffffffff)
        self.ack_num = ack_num
        self.flags = flags
        self.window = window
        self.build_raw()
    
    def build_raw(self, payload_length: int = 0) -> bytes:
        """Build TCP header."""
        # Header fields
        data_offset = 5  # 5 words = 20 bytes header
        reserved = 0
        header_checksum = 0
        urgent_pointer = 0
        
        # Build pseudo header for checksum (IPv4)
        # This is simplified - real checksum includes pseudo header
        # We'll calculate a simple checksum for demonstration
        
        header = struct.pack(
            "!HHLLBBHHH",
            self.src_port,
            self.dst_port,
            self.seq_num,
            self.ack_num,
            (data_offset << 4) | reserved,
            self.flags,
            self.window,
            header_checksum,
            urgent_pointer,
        )
        
        # Simple checksum (not full TCP checksum with pseudo header)
        # For educational purposes
        if payload_length > 0:
            # Just a placeholder for real checksum
            pass
        
        self.raw = header
        self.data["raw"] = header
        return header


class TCPBuilder(PacketBuilder):
    """TCP packet builder."""
    
    def __init__(self):
        super().__init__()
        self.packet.add_layer(
            PacketLayer(
                name="tcp",
                data={"builder": "TCPBuilder"}
            )
        )
    
    def build_header(
        self,
        src_port: Optional[int] = None,
        dst_port: Optional[int] = None,
        seq_num: Optional[int] = None,
        ack_num: int = 0,
        flags: int = 0x02,
        window: int = 65535,
        **kwargs
    ) -> bytes:
        """Build TCP header."""
        src_port = src_port or generate_port()
        dst_port = dst_port or generate_port()
        seq_num = seq_num or random.randint(0, 0xffffffff)
        
        # Validate ports
        if not validate_port(src_port) or not validate_port(dst_port):
            raise ValueError("Invalid port number")
        
        # Header
        data_offset = 5
        reserved = 0
        checksum = 0
        urgent_pointer = 0
        
        header = struct.pack(
            "!HHLLBBHHH",
            src_port,
            dst_port,
            seq_num,
            ack_num,
            (data_offset << 4) | reserved,
            flags,
            window,
            checksum,
            urgent_pointer,
        )
        
        # Store layer data
        layer_data = {
            "src_port": src_port,
            "dst_port": dst_port,
            "seq_num": seq_num,
            "ack_num": ack_num,
            "flags": flags,
            "window": window,
        }
        self.add_layer("tcp", layer_data, header)
        
        return header
    
    def build_payload(self, payload: bytes) -> bytes:
        """Build with payload."""
        # TCP payload is simply appended
        return payload
