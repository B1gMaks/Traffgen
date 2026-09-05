import pytest
from trafficlab.core.config import Config
from trafficlab.profiles import load_profile
from trafficlab.generators.packet_generator import PacketGenerator
from trafficlab.generators.session_generator import SessionGenerator
from trafficlab.generators.payload_generator import PayloadGenerator
from trafficlab.generators.timing import (
    FixedTiming,
    UniformTiming,
    NormalTiming,
    PoissonTiming,
    BurstTiming,
)
from trafficlab.core.types import ProtocolType


class TestTiming:
    """Test timing models."""
    
    def test_fixed_timing(self):
        """Test fixed timing."""
        timing = FixedTiming(interval=1.0)
        assert timing.next_interval() == 1.0
        interval, size = timing.next_burst()
        assert interval == 1.0
        assert size == 1
    
    def test_uniform_timing(self):
        """Test uniform timing."""
        timing = UniformTiming(min_interval=0.5, max_interval=2.0)
        interval = timing.next_interval()
        assert 0.5 <= interval <= 2.0
    
    def test_poisson_timing(self):
        """Test Poisson timing."""
        timing = PoissonTiming(mean=1.0)
        interval = timing.next_interval()
        assert interval > 0
    
    def test_burst_timing(self):
        """Test burst timing."""
        timing = BurstTiming(
            burst_interval=0.1,
            burst_size=10,
            idle_interval=5.0,
            idle_probability=0.0
        )
        # Should be in burst
        interval, size = timing.next_burst()
        assert interval == 0.1
        assert size == 10


class TestPayloadGenerator:
    """Test payload generator."""
    
    def test_generate_random(self):
        """Test random payload."""
        gen = PayloadGenerator()
        payload = gen.generate_payload(100, "random")
        assert len(payload) == 100
    
    def test_generate_lorem(self):
        """Test Lorem Ipsum payload."""
        gen = PayloadGenerator()
        payload = gen.generate_payload(100, "lorem")
        assert len(payload) == 100
        assert isinstance(payload, bytes)
    
    def test_generate_html(self):
        """Test HTML generation."""
        gen = PayloadGenerator()
        html = gen.generate_html()
        assert "<html" in html.lower()
    
    def test_generate_json(self):
        """Test JSON generation."""
        gen = PayloadGenerator()
        json_str = gen.generate_json()
        assert "{" in json_str
        assert "}" in json_str
    
    def test_generate_http_request(self):
        """Test HTTP request generation."""
        gen = PayloadGenerator()
        request = gen.generate_http_request()
        assert "HTTP/1.1" in request


class TestPacketGenerator:
    """Test packet generator."""
    
    def test_generate_packet(self):
        """Test packet generation."""
        config = Config()
        generator = PacketGenerator(config)
        packet = generator.generate(ProtocolType.HTTP)
        
        assert packet is not None
        assert packet.protocol == ProtocolType.HTTP
        assert len(packet.payload) > 0
    
    def test_generate_batch(self):
        """Test batch generation."""
        config = Config()
        generator = PacketGenerator(config)
        packets = generator.generate_batch(10)
        
        assert len(packets) == 10
        for packet in packets:
            assert packet is not None


class TestSessionGenerator:
    """Test session generator."""
    
    def test_generate_session(self):
        """Test session generation."""
        config = Config()
        profile = load_profile("enterprise")
        generator = SessionGenerator(profile, config)
        
        packets = list(generator.generate())
        # At least some packets
        assert len(packets) > 0
    
    def test_http_session(self):
        """Test HTTP session generation."""
        config = Config()
        profile = load_profile("enterprise")
        generator = SessionGenerator(profile, config)
        
        # Force HTTP pattern
        packets = generator._generate_http_session(5)
        assert len(packets) > 0
        for packet in packets:
            assert packet.protocol == ProtocolType.HTTP
    
    def test_dns_session(self):
        """Test DNS session generation."""
        config = Config()
        profile = load_profile("enterprise")
        generator = SessionGenerator(profile, config)
        
        packets = generator._generate_dns_session(4)
        assert len(packets) > 0
    
    def test_dhcp_session(self):
        """Test DHCP session generation."""
        config = Config()
        profile = load_profile("enterprise")
        generator = SessionGenerator(profile, config)
        
        packets = generator._generate_dhcp_session()
        assert len(packets) == 4  # DORA
