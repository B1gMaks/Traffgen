from typing import Dict, Any, Optional
import struct
from ..packets.builder import PacketBuilder
from ..packets.packet import PacketLayer
from ..common.utils import generate_mac


class EthernetLayer(PacketLayer):
    """Ethernet II layer."""
    
    def __init__(
        self,
        dst_mac: str,
        src_mac: str,
        ethertype: int = 0x0800,
        data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name="ethernet",
            data={
                "dst_mac": dst_mac,
                "src_mac": src_mac,
                "ethertype": ethertype,
                **(data or {}),
            }
        )
        self.dst_mac = dst_mac
        self.src_mac = src_mac
        self.ethertype = ethertype
        self.build_raw()
    
    def build_raw(self) -> bytes:
        """Build raw Ethernet frame."""
        # Parse MAC addresses
        dst_bytes = bytes.fromhex(self.dst_mac.replace(":", ""))
        src_bytes = bytes.fromhex(self.src_mac.replace(":", ""))
        
        # Build frame: dst(6) + src(6) + ethertype(2)
        self.raw = dst_bytes + src_bytes + struct.pack("!H", self.ethertype)
        self.data["raw"] = self.raw
        return self.raw


class EthernetBuilder(PacketBuilder):
    """Ethernet packet builder."""
    
    def __init__(self):
        super().__init__()
        self.packet.add_layer(
            PacketLayer(
                name="ethernet",
                data={"builder": "EthernetBuilder"}
            )
        )
    
    def build_header(
        self,
        src: Optional[str] = None,
        dst: Optional[str] = None,
        ethertype: int = 0x0800,
        **kwargs
    ) -> bytes:
        """Build Ethernet header."""
        src = src or generate_mac()
        dst = dst or generate_mac()
        
        # Convert to bytes
        dst_bytes = bytes.fromhex(dst.replace(":", ""))
        src_bytes = bytes.fromhex(src.replace(":", ""))
        
        header = dst_bytes + src_bytes + struct.pack("!H", ethertype)
        
        # Store layer data
        layer_data = {
            "src": src,
            "dst": dst,
            "ethertype": ethertype,
        }
        self.add_layer("ethernet", layer_data, header)
        
        return header
    
    def build_payload(self, payload: bytes) -> bytes:
        """Build with payload."""
        # Ethernet doesn't have payload processing
        # We just append payload after header
        return payload
