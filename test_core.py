import pytest
from pathlib import Path
import tempfile
import json

from trafficlab.core.config import Config, ProtocolMix, TopologyConfig
from trafficlab.core.types import Address, PacketData, ProtocolType
from trafficlab.core.registry import Registry


class TestConfig:
    """Test configuration."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = Config()
        assert config.profile == "enterprise"
        assert config.duration == 3600
        assert isinstance(config.protocol_mix, ProtocolMix)
        assert isinstance(config.topology, TopologyConfig)
    
    def test_config_from_yaml(self):
        """Test loading config from YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
profile: office
duration: 1800
average_packet_size: 1024
""")
            f.flush()
            
            config = Config.from_yaml(Path(f.name))
            assert config.profile == "office"
            assert config.duration == 1800
            assert config.average_packet_size == 1024
    
    def test_config_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValueError):
            Config(duration=-1)
    
    def test_protocol_mix_total(self):
        """Test protocol mix total."""
        mix = ProtocolMix()
        assert mix.get_total() == sum(v for v in mix.__dict__.values())


class TestTypes:
    """Test type definitions."""
    
    def test_address(self):
        """Test Address creation."""
        addr = Address(ipv4="192.168.1.1", port=8080)
        assert addr.ipv4 == "192.168.1.1"
        assert addr.port == 8080
    
    def test_packet_data(self):
        """Test PacketData creation."""
        src = Address(ipv4="192.168.1.1")
        dst = Address(ipv4="192.168.1.2")
        
        packet = PacketData(
            source=src,
            destination=dst,
            protocol=ProtocolType.HTTP,
            payload=b"GET / HTTP/1.1",
            length=20,
        )
        
        assert packet.source.ipv4 == "192.168.1.1"
        assert packet.protocol == ProtocolType.HTTP
        assert packet.length == 20


class TestRegistry:
    """Test registry."""
    
    def test_registry_singleton(self):
        """Test registry is singleton."""
        reg1 = Registry()
        reg2 = Registry()
        assert reg1 is reg2
    
    def test_register_protocol(self):
        """Test protocol registration."""
        registry = Registry()
        
        @registry.register_protocol("test_protocol")
        class TestProtocol:
            pass
        
        assert registry.get_protocol("test_protocol") == TestProtocol
        assert "test_protocol" in registry.list_protocols()
    
    def test_register_exporter(self):
        """Test exporter registration."""
        registry = Registry()
        
        @registry.register_exporter("test_exporter")
        class TestExporter:
            pass
        
        assert registry.get_exporter("test_exporter") == TestExporter
