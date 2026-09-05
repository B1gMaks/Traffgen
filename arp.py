"""ARP layer implementation."""

from typing import Optional, Dict, Any
import struct
from ..packets.builder import PacketBuilder
from ..packets.packet import PacketLayer
from ..common.utils import generate_mac, generate_ipv4


class ARPLayer(PacketLayer):
    """ARP layer."""
    
    def __init__(
        self,
        opcode: int = 1,  # 1=request, 2=reply
        src_mac: Optional[str] = None,
        src_ip: Optional[str] = None,
        dst_mac: Optional[str] = None,
        dst_ip: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name="arp",
            data={
                "opcode": opcode,
                "src_mac": src_mac or generate_mac(),
                "src_ip": src_ip or generate_ipv4(),
                "dst_mac": dst_mac or "00:00:00:00:00:00",
                "dst_ip": dst_ip or generate_ipv4(),
                **(data or {}),
            }
        )
        self.opcode = opcode
        self.src_mac = data.get("src_mac", generate_mac())
        self.src_ip = data.get("src_ip", generate_ipv4())
        self.dst_mac = data.get("dst_mac", "00:00:00:00:00:00")
        self.dst_ip = data.get("dst_ip", generate_ipv4())
        self.build_raw()
    
    def build_raw(self) -> bytes:
        """Build ARP header."""
        # Hardware type: Ethernet (1)
        htype = 1
        # Protocol type: IPv4 (0x0800)
        ptype = 0x0800
        # Hardware address length: 6
        hlen = 6
        # Protocol address length: 4
        plen = 4
        
        # Parse addresses
        src_mac_bytes = bytes.fromhex(self.src_mac.replace(":", ""))
        src_ip_bytes = bytes(map(int, self.src_ip.split('.')))
        dst_mac_bytes = bytes.fromhex(self.dst_mac.replace(":", ""))
        dst_ip_bytes = bytes(map(int, self.dst_ip.split('.')))
        
        header = struct.pack(
            "!HHBBH",
            htype,
            ptype,
            hlen,
            plen,
            self.opcode,
        ) + src_mac_bytes + src_ip_bytes + dst_mac_bytes + dst_ip_bytes
        
        self.raw = header
        self.data["raw"] = header
        return header


class ARPBuilder(PacketBuilder):
    """ARP packet builder."""
    
    def __init__(self):
        super().__init__()
        self.packet.add_layer(
            PacketLayer(
                name="arp",
                data={"builder": "ARPBuilder"}
            )
        )
    
    def build_header(
        self,
        opcode: int = 1,
        src_mac: Optional[str] = None,
        src_ip: Optional[str] = None,
        dst_mac: Optional[str] = None,
        dst_ip: Optional[str] = None,
        **kwargs
    ) -> bytes:
        """Build ARP header."""
        src_mac = src_mac or generate_mac()
        src_ip = src_ip or generate_ipv4()
        dst_mac = dst_mac or "00:00:00:00:00:00"
        dst_ip = dst_ip or generate_ipv4()
        
        # Parse addresses
        src_mac_bytes = bytes.fromhex(src_mac.replace(":", ""))
        src_ip_bytes = bytes(map(int, src_ip.split('.')))
        dst_mac_bytes = bytes.fromhex(dst_mac.replace(":", ""))
        dst_ip_bytes = bytes(map(int, dst_ip.split('.')))
        
        htype = 1  # Ethernet
        ptype = 0x0800  # IPv4
        hlen = 6
        plen = 4
        
        header = struct.pack(
            "!HHBBH",
            htype,
            ptype,
            hlen,
            plen,
            opcode,
        ) + src_mac_bytes + src_ip_bytes + dst_mac_bytes + dst_ip_bytes
        
        # Store layer data
        layer_data = {
            "opcode": opcode,
            "src_mac": src_mac,
            "src_ip": src_ip,
            "dst_mac": dst_mac,
            "dst_ip": dst_ip,
        }
        self.add_layer("arp", layer_data, header)
        
        return header
    
    def build_payload(self, payload: bytes) -> bytes:
        """Build with payload."""
        # ARP doesn't have payload
        return payload
