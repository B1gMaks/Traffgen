from typing import Iterator, List, Optional, Dict, Any
import random
from datetime import datetime, timedelta
from .base import Generator
from .packet_generator import PacketGenerator
from .payload_generator import PayloadGenerator
from .timing import PoissonTiming
from ..core.types import PacketData, SessionData, FlowData, ProtocolType, Address
from ..profiles.base import Profile
from ..core.config import Config
from ..common.utils import generate_ipv4, generate_mac, generate_port


class SessionGenerator(Generator):
    """Generate protocol sessions."""
    
    def __init__(
        self,
        profile: Profile,
        config: Config,
        timing: Optional[PoissonTiming] = None,
    ):
        super().__init__(config, profile)
        self.timing = timing or PoissonTiming(
            mean=config.timing.mean_interval,
            burst_factor=config.timing.burst_factor,
        )
        self.packet_generator = PacketGenerator(config)
        self.payload_generator = PayloadGenerator()
        self._session_counter = 0
    
    def generate(self) -> Iterator[PacketData]:
        """Generate packet sessions."""
        self.initialize()
        
        # Get traffic patterns from profile
        patterns = self.profile.traffic_patterns if self.profile else []
        
        # Generate packets based on traffic patterns
        while True:
            # Select a random pattern weighted by its weight
            if patterns:
                pattern = random.choices(
                    patterns,
                    weights=[p.weight for p in patterns],
                    k=1
                )[0]
            else:
                # Default to HTTP if no pattern
                from ..core.types import ProtocolType
                pattern = type('Pattern', (), {
                    'protocol': ProtocolType.HTTP,
                    'packet_size': 512,
                    'rate': 10.0,
                    'session_length': 5,
                    'timing_distribution': 'poisson'
                })()
            
            # Generate session for this pattern
            session_packets = self._generate_session(pattern)
            
            for packet in session_packets:
                yield packet
            
            # Break condition will be handled by engine
    
    def _generate_session(self, pattern) -> List[PacketData]:
        """Generate a single session."""
        packets = []
        
        # Determine session length
        if hasattr(pattern, 'session_length'):
            length = pattern.session_length
        else:
            length = self.config.session_length
        
        # Add variation
        length = max(1, length + random.randint(-2, 2))
        
        # Create session
        protocol = pattern.protocol
        
        # Generate conversation based on protocol type
        if protocol == ProtocolType.HTTP:
            packets = self._generate_http_session(length)
        elif protocol == ProtocolType.HTTPS:
            packets = self._generate_https_session(length)
        elif protocol == ProtocolType.DNS:
            packets = self._generate_dns_session(length)
        elif protocol == ProtocolType.DHCP:
            packets = self._generate_dhcp_session()
        elif protocol == ProtocolType.SMTP:
            packets = self._generate_smtp_session(length)
        elif protocol == ProtocolType.MQTT:
            packets = self._generate_mqtt_session(length)
        elif protocol == ProtocolType.NTP:
            packets = self._generate_ntp_session()
        else:
            # Generic session
            packets = self._generate_generic_session(protocol, length)
        
        return packets
    
    def _generate_http_session(self, length: int) -> List[PacketData]:
        """Generate HTTP session."""
        packets = []
        
        # Client and server addresses
        src = Address(ipv4=generate_ipv4(), port=generate_port())
        dst = Address(ipv4=generate_ipv4(), port=80)
        
        # HTTP request
        for i in range(length):
            if i == 0:
                # Request
                payload = self.payload_generator.generate_http_request()
                packet = self.packet_generator.generate(
                    protocol=ProtocolType.HTTP,
                    source=src,
                    destination=dst,
                    payload=payload.encode(),
                )
                packets.append(packet)
            else:
                # Response
                payload = self.payload_generator.generate_http_response()
                packet = self.packet_generator.generate(
                    protocol=ProtocolType.HTTP,
                    source=dst,
                    destination=src,
                    payload=payload.encode(),
                )
                packets.append(packet)
        
        return packets
    
    def _generate_https_session(self, length: int) -> List[PacketData]:
        """Generate HTTPS session with TLS handshake."""
        packets = []
        
        src = Address(ipv4=generate_ipv4(), port=generate_port())
        dst = Address(ipv4=generate_ipv4(), port=443)
        
        # TLS handshake - simplified
        from ..protocols.tls import generate_tls_client_hello, generate_tls_server_hello
        
        # Client Hello
        hello = generate_tls_client_hello()
        packet = self.packet_generator.generate(
            protocol=ProtocolType.TLS,
            source=src,
            destination=dst,
            payload=hello,
        )
        packets.append(packet)
        
        # Server Hello
        hello = generate_tls_server_hello()
        packet = self.packet_generator.generate(
            protocol=ProtocolType.TLS,
            source=dst,
            destination=src,
            payload=hello,
        )
        packets.append(packet)
        
        # HTTP over TLS
        for i in range(length - 2):
            if i % 2 == 0:
                payload = self.payload_generator.generate_http_request().encode()
                packet = self.packet_generator.generate(
                    protocol=ProtocolType.HTTPS,
                    source=src,
                    destination=dst,
                    payload=payload,
                )
            else:
                payload = self.payload_generator.generate_http_response().encode()
                packet = self.packet_generator.generate(
                    protocol=ProtocolType.HTTPS,
                    source=dst,
                    destination=src,
                    payload=payload,
                )
            packets.append(packet)
        
        return packets
    
    def _generate_dns_session(self, length: int) -> List[PacketData]:
        """Generate DNS session."""
        packets = []
        
        src = Address(ipv4=generate_ipv4(), port=generate_port())
        dst = Address(ipv4=generate_ipv4(), port=53)
        
        from ..protocols.dns import generate_dns_query, generate_dns_response
        
        for i in range(length):
            if i % 2 == 0:
                # Query
                payload = generate_dns_query()
                packet = self.packet_generator.generate(
                    protocol=ProtocolType.DNS,
                    source=src,
                    destination=dst,
                    payload=payload,
                )
            else:
                # Response
                payload = generate_dns_response()
                packet = self.packet_generator.generate(
                    protocol=ProtocolType.DNS,
                    source=dst,
                    destination=src,
                    payload=payload,
                )
            packets.append(packet)
        
        return packets
    
    def _generate_dhcp_session(self) -> List[PacketData]:
        """Generate DHCP DORA session."""
        packets = []
        
        src = Address(ipv4=generate_ipv4(), port=68)
        dst = Address(ipv4="255.255.255.255", port=67)
        
        from ..protocols.dhcp import (
            generate_dhcp_discover,
            generate_dhcp_offer,
            generate_dhcp_request,
            generate_dhcp_ack,
        )
        
        # DORA: Discover -> Offer -> Request -> ACK
        packets.append(self.packet_generator.generate(
            protocol=ProtocolType.DHCP,
            source=src,
            destination=dst,
            payload=generate_dhcp_discover(),
        ))
        
        packets.append(self.packet_generator.generate(
            protocol=ProtocolType.DHCP,
            source=dst,
            destination=src,
            payload=generate_dhcp_offer(),
        ))
        
        packets.append(self.packet_generator.generate(
            protocol=ProtocolType.DHCP,
            source=src,
            destination=dst,
            payload=generate_dhcp_request(),
        ))
        
        packets.append(self.packet_generator.generate(
            protocol=ProtocolType.DHCP,
            source=dst,
            destination=src,
            payload=generate_dhcp_ack(),
        ))
        
        return packets
    
    def _generate_smtp_session(self, length: int) -> List[PacketData]:
        """Generate SMTP session."""
        packets = []
        
        src = Address(ipv4=generate_ipv4(), port=generate_port())
        dst = Address(ipv4=generate_ipv4(), port=25)
        
        from ..protocols.smtp import generate_smtp_commands
        
        for i in range(length):
            if i % 2 == 0:
                # Client command
                payload = generate_smtp_commands()
                packet = self.packet_generator.generate(
                    protocol=ProtocolType.SMTP,
                    source=src,
                    destination=dst,
                    payload=payload.encode(),
                )
            else:
                # Server response
                from ..payload_generator import generate_smtp_response
                payload = generate_smtp_response()
                packet = self.packet_generator.generate(
                    protocol=ProtocolType.SMTP,
                    source=dst,
                    destination=src,
                    payload=payload.encode(),
                )
            packets.append(packet)
        
        return packets
    
    def _generate_mqtt_session(self, length: int) -> List[PacketData]:
        """Generate MQTT session."""
        packets = []
        
        src = Address(ipv4=generate_ipv4(), port=generate_port())
        dst = Address(ipv4=generate_ipv4(), port=1883)
        
        from ..protocols.mqtt import generate_mqtt_publish, generate_mqtt_subscribe
        
        for i in range(length):
            if i == 0:
                # Subscribe
                payload = generate_mqtt_subscribe()
                packet = self.packet_generator.generate(
                    protocol=ProtocolType.MQTT,
                    source=src,
                    destination=dst,
                    payload=payload,
                )
            elif i % 2 == 0:
                # Publish
                payload = generate_mqtt_publish()
                packet = self.packet_generator.generate(
                    protocol=ProtocolType.MQTT,
                    source=src,
                    destination=dst,
                    payload=payload,
                )
            else:
                # Publish response
                payload = generate_mqtt_publish()
                packet = self.packet_generator.generate(
                    protocol=ProtocolType.MQTT,
                    source=dst,
                    destination=src,
                    payload=payload,
                )
            packets.append(packet)
        
        return packets
    
    def _generate_ntp_session(self) -> List[PacketData]:
        """Generate NTP session."""
        packets = []
        
        src = Address(ipv4=generate_ipv4(), port=generate_port())
        dst = Address(ipv4=generate_ipv4(), port=123)
        
        from ..protocols.ntp import generate_ntp_request, generate_ntp_response
        
        # Request
        packets.append(self.packet_generator.generate(
            protocol=ProtocolType.NTP,
            source=src,
            destination=dst,
            payload=generate_ntp_request(),
        ))
        
        # Response
        packets.append(self.packet_generator.generate(
            protocol=ProtocolType.NTP,
            source=dst,
            destination=src,
            payload=generate_ntp_response(),
        ))
        
        return packets
    
    def _generate_generic_session(self, protocol: ProtocolType, length: int) -> List[PacketData]:
        """Generate generic session."""
        packets = []
        
        src = Address(ipv4=generate_ipv4(), port=generate_port())
        dst = Address(ipv4=generate_ipv4(), port=generate_port())
        
        for i in range(length):
            payload = self.payload_generator.generate_payload(
                size=random.randint(64, 1500),
                pattern="random"
            )
            packet = self.packet_generator.generate(
                protocol=protocol,
                source=src,
                destination=dst,
                payload=payload,
            )
            packets.append(packet)
        
        return packets
    
    async def generate_async(self) -> List[PacketData]:
        """Generate sessions asynchronously."""
        packets = []
        for packet in self.generate():
            packets.append(packet)
        return packets
