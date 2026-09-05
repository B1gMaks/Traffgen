from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from .packet import Packet, PacketLayer


class PacketBuilder(ABC):
    """Abstract packet builder."""
    
    def __init__(self):
        self.packet = Packet()
        self._current_layer: Optional[PacketLayer] = None
    
    @abstractmethod
    def build_header(self, **kwargs) -> bytes:
        """Build header bytes."""
        pass
    
    @abstractmethod
    def build_payload(self, payload: bytes) -> bytes:
        """Build with payload."""
        pass
    
    def build(self, **kwargs) -> Packet:
        """Build complete packet."""
        raw = self.build_header(**kwargs)
        if "payload" in kwargs:
            raw += self.build_payload(kwargs["payload"])
        
        self.packet.raw_data = raw
        self.packet.length = len(raw)
        return self.packet
    
    def add_layer(self, name: str, data: Dict[str, Any], raw: bytes) -> None:
        """Add layer to packet."""
        layer = PacketLayer(name=name, data=data, raw=raw)
        self.packet.add_layer(layer)
