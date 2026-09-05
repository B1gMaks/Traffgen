from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel


class PacketLayer(BaseModel):
    """Base layer model."""
    
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    raw: Optional[bytes] = None
    next_layer: Optional[str] = None


class Packet(BaseModel):
    """Base packet model."""
    
    timestamp: datetime = field(default_factory=datetime.now)
    layers: List[PacketLayer] = field(default_factory=list)
    raw_data: bytes = b""
    length: int = 0
    
    def add_layer(self, layer: PacketLayer) -> None:
        """Add a layer to the packet."""
        self.layers.append(layer)
        self.length += len(layer.raw) if layer.raw else 0
    
    def get_layer(self, name: str) -> Optional[PacketLayer]:
        """Get a layer by name."""
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None
    
    def get_protocol(self) -> Optional[str]:
        """Get the highest protocol."""
        if self.layers:
            return self.layers[-1].name
        return None
    
    def build(self) -> bytes:
        """Build packet to bytes."""
        if self.raw_data:
            return self.raw_data
        
        # Build from layers (bottom to top)
        result = b""
        for layer in reversed(self.layers):
            if layer.raw:
                result = layer.raw + result
            else:
                # Layer should provide build method
                pass
        
        self.raw_data = result
        self.length = len(result)
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert packet to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "layers": [l.dict() for l in self.layers],
            "length": self.length,
            "protocol": self.get_protocol(),
        }
    
    class Config:
        arbitrary_types_allowed = True
