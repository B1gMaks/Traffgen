from typing import Dict, List, Optional, Any, Union
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel, Field, IPvAnyAddress


class ProtocolType(str, Enum):
    """Network protocol types."""
    ETHERNET = "ethernet"
    IEEE8023 = "ieee8023"
    LLC = "llc"
    SNAP = "snap"
    ARP = "arp"
    RARP = "rarp"
    VLAN = "vlan"
    QINQ = "qinq"
    LLDP = "lldp"
    CDP = "cdp"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    ICMP = "icmp"
    ICMPV6 = "icmpv6"
    IGMP = "igmp"
    TCP = "tcp"
    UDP = "udp"
    SCTP = "sctp"
    DCCP = "dccp"
    GRE = "gre"
    MPLS = "mpls"
    VXLAN = "vxlan"
    GENEVE = "geneve"
    DNS = "dns"
    DHCP = "dhcp"
    HTTP = "http"
    HTTPS = "https"
    TLS = "tls"
    SMTP = "smtp"
    MQTT = "mqtt"
    NTP = "ntp"
    WEBSOCKET = "websocket"


class ProfileType(str, Enum):
    """Network profile types."""
    OFFICE = "office"
    ENTERPRISE = "enterprise"
    HOME = "home"
    UNIVERSITY = "university"
    IOT = "iot"
    CLOUD = "cloud"
    DATACENTER = "datacenter"
    ISP = "isp"
    INDUSTRIAL = "industrial"
    TELECOM = "telecom"


@dataclass
class Address:
    """Network address representation."""
    mac: Optional[str] = None
    ipv4: Optional[str] = None
    ipv6: Optional[str] = None
    port: Optional[int] = None
    hostname: Optional[str] = None
    
    @classmethod
    def from_string(cls, addr_str: str) -> "Address":
        """Parse address from string."""
        # Simple parsing logic
        parts = addr_str.split(":")
        return cls(
            mac=parts[0] if len(parts) > 0 else None,
            ipv4=parts[1] if len(parts) > 1 else None,
            port=int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None,
        )


class PacketData(BaseModel):
    """Packet data model."""
    timestamp: datetime = Field(default_factory=datetime.now)
    source: Address
    destination: Address
    protocol: ProtocolType
    payload: bytes
    length: int
    layers: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class FlowData(BaseModel):
    """Flow data model."""
    flow_id: str
    source: Address
    destination: Address
    protocol: ProtocolType
    packets: List[PacketData] = Field(default_factory=list)
    start_time: datetime
    end_time: Optional[datetime] = None
    packet_count: int = 0
    byte_count: int = 0
    duration: float = 0.0
    
    def add_packet(self, packet: PacketData) -> None:
        """Add packet to flow."""
        self.packets.append(packet)
        self.packet_count += 1
        self.byte_count += packet.length
        self.end_time = packet.timestamp
        if self.packet_count > 1:
            self.duration = (self.end_time - self.start_time).total_seconds()


class SessionData(BaseModel):
    """Session data model."""
    session_id: str
    flows: List[FlowData] = Field(default_factory=list)
    start_time: datetime
    end_time: Optional[datetime] = None
    total_packets: int = 0
    total_bytes: int = 0
    protocol_mix: Dict[ProtocolType, int] = Field(default_factory=dict)
    
    def add_flow(self, flow: FlowData) -> None:
        """Add flow to session."""
        self.flows.append(flow)
        self.total_packets += flow.packet_count
        self.total_bytes += flow.byte_count
        self.end_time = flow.end_time or self.end_time
        protocol = flow.protocol
        self.protocol_mix[protocol] = self.protocol_mix.get(protocol, 0) + flow.packet_count
