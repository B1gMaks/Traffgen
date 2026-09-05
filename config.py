from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class ProtocolMix(BaseModel):
    """Protocol mix configuration."""
    dns: int = 10
    http: int = 20
    https: int = 15
    smtp: int = 5
    mqtt: int = 5
    ntp: int = 5
    snmp: int = 5
    dhcp: int = 5
    ftp: int = 3
    tls: int = 10
    
    def get_total(self) -> int:
        """Get total weight."""
        return sum(v for v in self.__dict__.values())


class OutputConfig(BaseModel):
    """Output configuration."""
    
    format: str = "pcap"
    filename: str = "traffic.pcap"
    compression: bool = False
    max_size: Optional[int] = None


class TimingConfig(BaseModel):
    """Timing configuration."""
    distribution: str = "poisson"  # fixed, uniform, normal, poisson
    mean_interval: float = 1.0  # seconds
    std_deviation: float = 0.3
    burst_factor: float = 0.0
    idle_periods: List[Dict[str, str]] = Field(default_factory=list)
    office_hours: bool = False
    weekend_profile: bool = False
    night_traffic_reduction: float = 0.0


class TopologyConfig(BaseModel):
    """Topology configuration."""
    routers: int = 5
    switches: int = 10
    servers: int = 20
    clients: int = 100
    iot_devices: int = 10
    printers: int = 5
    nas_devices: int = 2
    dns_servers: int = 2
    dhcp_servers: int = 1
    mail_servers: int = 2
    web_servers: int = 5
    database_servers: int = 3


class Config(BaseSettings):
    """Main configuration model."""
    # General
    profile: str = "enterprise"
    duration: int = 3600  # seconds
    seed: Optional[int] = None
    
    # Topology
    topology: TopologyConfig = Field(default_factory=TopologyConfig)
    
    # Traffic
    protocol_mix: ProtocolMix = Field(default_factory=ProtocolMix)
    average_packet_size: int = 512
    session_length: int = 10  # average packets per session
    
    # Timing
    timing: TimingConfig = Field(default_factory=TimingConfig)
    
    # Output
    output: OutputConfig = Field(default_factory=OutputConfig)
    
    # Advanced
    background_traffic: bool = True
    error_generation: float = 0.01  # 1% error packets
    burst_mode: bool = False
    
    class Config:
        env_prefix = "TRAFFICLAB_"
        env_nested_delimiter = "__"
    
    @validator("duration")
    def validate_duration(cls, v: int) -> int:
        """Validate duration is positive."""
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v
    
    @classmethod
    def from_yaml(cls, path: Path) -> "Config":
        """Load configuration from YAML file."""
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
    
    def to_yaml(self, path: Path) -> None:
        """Save configuration to YAML file."""
        data = self.dict()
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
