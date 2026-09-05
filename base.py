from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from ..core.types import ProtocolType


class HostType(str, Enum):
    """Host types."""
    CLIENT = "client"
    SERVER = "server"
    ROUTER = "router"
    SWITCH = "switch"
    PRINTER = "printer"
    IOT = "iot"
    NAS = "nas"
    DNS = "dns"
    DHCP = "dhcp"
    MAIL = "mail"
    WEB = "web"
    DATABASE = "database"
    MONITORING = "monitoring"
    NTP = "ntp"


@dataclass
class Host:
    """Host in a network profile."""
    
    name: str
    host_type: HostType
    ip_range: str
    count: int = 1
    services: List[str] = field(default_factory=list)
    os: str = "Linux"
    version: str = "5.15"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Service:
    """Service running on a host."""
    
    name: str
    protocol: ProtocolType
    port: int
    version: str = "1.0"
    tls_enabled: bool = False
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrafficPattern:
    """Traffic pattern definition."""
    
    name: str
    protocol: ProtocolType
    weight: int = 10
    packet_size: int = 512
    rate: float = 10.0  # packets per second
    burst_factor: float = 0.0
    session_length: int = 5
    timing_distribution: str = "poisson"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Profile:
    """Base network profile."""
    
    name: str
    description: str = ""
    hosts: List[Host] = field(default_factory=list)
    services: List[Service] = field(default_factory=list)
    traffic_patterns: List[TrafficPattern] = field(default_factory=list)
    subnets: List[str] = field(default_factory=list)
    
    def get_hosts_by_type(self, host_type: HostType) -> List[Host]:
        """Get hosts of a specific type."""
        return [h for h in self.hosts if h.host_type == host_type]
    
    def get_total_hosts(self) -> int:
        """Get total number of hosts."""
        return sum(h.count for h in self.hosts)
    
    def get_traffic_by_protocol(self, protocol: ProtocolType) -> List[TrafficPattern]:
        """Get traffic patterns for a protocol."""
        return [t for t in self.traffic_patterns if t.protocol == protocol]
    
    def get_services_by_host(self, host_name: str) -> List[Service]:
        """Get services for a host."""
        # Find host
        for host in self.hosts:
            if host.name == host_name:
                return [s for s in self.services if s.name in host.services]
        return []
