from typing import Optional, Dict, Any
import random
from datetime import datetime
from .base import Generator
from ..core.types import PacketData, Address, ProtocolType
from ..core.config import Config
from ..packets.factory import PacketFactory
from ..common.utils import generate_ipv4, generate_mac, generate_port


class PacketGenerator(Generator):
    """Generate individual packets."""
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.factory = PacketFactory()
    
    def generate(
        self,
        protocol: ProtocolType,
        source: Optional[Address] = None,
        destination: Optional[Address] = None,
        payload: Optional[bytes] = None,
        **kwargs
    ) -> PacketData:
        """Generate a single packet."""
        # Fill missing addresses
        if source is None:
            source = Address(
                mac=generate_mac(),
                ipv4=generate_ipv4(),
                port=generate_port(),
            )
        
        if destination is None:
            destination = Address(
                mac=generate_mac(),
                ipv4=generate_ipv4(),
                port=generate_port(),
            )
        
        # Generate payload if not provided
        if payload is None:
            payload = self._generate_payload(protocol, **kwargs)
        
        # Build packet
        packet = self.factory.create(
            protocol.value,
            src=source.ipv4 or source.mac,
            dst=destination.ipv4 or destination.mac,
            payload=payload,
            **kwargs
        )
        
        # Create PacketData
        packet_data = PacketData(
            timestamp=datetime.now(),
            source=source,
            destination=destination,
            protocol=protocol,
            payload=payload,
            length=len(packet.raw_data),
            layers={layer.name: layer.data for layer in packet.layers},
        )
        
        return packet_data
    
    def _generate_payload(self, protocol: ProtocolType, **kwargs) -> bytes:
        """Generate payload for protocol."""
        from .payload_generator import PayloadGenerator
        gen = PayloadGenerator()
        
        if protocol == ProtocolType.HTTP:
            return gen.generate_http_request().encode()
        elif protocol == ProtocolType.DNS:
            from ..protocols.dns import generate_dns_query
            return generate_dns_query()
        elif protocol == ProtocolType.DHCP:
            from ..protocols.dhcp import generate_dhcp_discover
            return generate_dhcp_discover()
        else:
            # Random payload
            size = kwargs.get("size", random.randint(64, 1500))
            return gen.generate_payload(size)
    
    def generate_batch(self, count: int) -> list:
        """Generate multiple packets."""
        packets = []
        for _ in range(count):
            protocol = random.choice(list(ProtocolType))
            packet = self.generate(protocol)
            packets.append(packet)
        return packets
    
    def generate_stream(self, count: int):
        """Generate a stream of packets."""
        for _ in range(count):
            protocol = random.choice(list(ProtocolType))
            yield self.generate(protocol)
    
    async def generate_async(self) -> list:
        """Generate packets asynchronously."""
        # Not implemented for individual packet generator
        return []
