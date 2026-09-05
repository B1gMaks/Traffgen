from typing import Dict, Any, Optional, Type
from .packet import Packet
from .builder import PacketBuilder
from ..core.registry import Registry


class PacketFactory:
    """Factory for creating packets."""
    
    def __init__(self):
        self.registry = Registry()
        self._builders: Dict[str, Type[PacketBuilder]] = {}
    
    def register_builder(self, protocol: str, builder_class: Type[PacketBuilder]) -> None:
        """Register a builder for a protocol."""
        self._builders[protocol] = builder_class
    
    def create(self, protocol: str, **kwargs) -> Packet:
        """Create a packet for the specified protocol."""
        builder_class = self._builders.get(protocol) or self.registry.get_builder(protocol)
        
        if not builder_class:
            raise ValueError(f"Unknown protocol: {protocol}")
        
        builder = builder_class()
        return builder.build(**kwargs)
    
    def create_ethernet(self, src_mac: str, dst_mac: str, payload: bytes, **kwargs) -> Packet:
        """Create Ethernet packet."""
        from ..layers.ethernet import EthernetBuilder
        builder = EthernetBuilder()
        return builder.build(src=src_mac, dst=dst_mac, payload=payload, **kwargs)
    
    def create_ipv4(self, src_ip: str, dst_ip: str, payload: bytes, **kwargs) -> Packet:
        """Create IPv4 packet."""
        from ..layers.ipv4 import IPv4Builder
        builder = IPv4Builder()
        return builder.build(src=src_ip, dst=dst_ip, payload=payload, **kwargs)
    
    def create_tcp(self, src_port: int, dst_port: int, payload: bytes, **kwargs) -> Packet:
        """Create TCP packet."""
        from ..layers.tcp import TCPBuilder
        builder = TCPBuilder()
        return builder.build(src_port=src_port, dst_port=dst_port, payload=payload, **kwargs)
    
    def create_udp(self, src_port: int, dst_port: int, payload: bytes, **kwargs) -> Packet:
        """Create UDP packet."""
        from ..layers.udp import UDPBuilder
        builder = UDPBuilder()
        return builder.build(src_port=src_port, dst_port=dst_port, payload=payload, **kwargs)
