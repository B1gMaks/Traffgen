import pytest
from trafficlab.packets.packet import Packet, PacketLayer
from trafficlab.packets.builder import PacketBuilder
from trafficlab.packets.factory import PacketFactory
from trafficlab.layers.ethernet import EthernetBuilder, EthernetLayer
from trafficlab.layers.ipv4 import IPv4Builder, IPv4Layer
from trafficlab.layers.tcp import TCPBuilder, TCPLayer
from trafficlab.layers.udp import UDPBuilder, UDPLayer
from trafficlab.layers.arp import ARPBuilder, ARPLayer


class TestPacket:
    """Test packet class."""
    
    def test_packet_creation(self):
        """Test packet creation."""
        packet = Packet()
        assert packet.layers == []
        assert packet.raw_data == b""
        assert packet.length == 0
    
    def test_add_layer(self):
        """Test adding layers."""
        packet = Packet()
        layer = PacketLayer(name="ethernet", raw=b"\x00" * 14)
        packet.add_layer(layer)
        
        assert len(packet.layers) == 1
        assert packet.length == 14
    
    def test_get_layer(self):
        """Test getting layer."""
        packet = Packet()
        layer = PacketLayer(name="ethernet", raw=b"\x00" * 14)
        packet.add_layer(layer)
        
        result = packet.get_layer("ethernet")
        assert result is not None
        assert result.name == "ethernet"
    
    def test_build(self):
        """Test building packet."""
        packet = Packet()
        layer = PacketLayer(name="ethernet", raw=b"\x00" * 14)
        packet.add_layer(layer)
        
        result = packet.build()
        assert result == b"\x00" * 14
        assert packet.length == 14


class TestEthernet:
    """Test Ethernet layer."""
    
    def test_ethernet_builder(self):
        """Test Ethernet builder."""
        builder = EthernetBuilder()
        header = builder.build_header(
            src="00:11:22:33:44:55",
            dst="66:77:88:99:aa:bb",
            ethertype=0x0800
        )
        
        assert len(header) == 14
        assert header[:6] == bytes.fromhex("66778899aabb")
        assert header[6:12] == bytes.fromhex("001122334455")
    
    def test_ethernet_layer(self):
        """Test Ethernet layer."""
        layer = EthernetLayer(
            dst_mac="66:77:88:99:aa:bb",
            src_mac="00:11:22:33:44:55",
            ethertype=0x0800
        )
        
        assert layer.dst_mac == "66:77:88:99:aa:bb"
        assert layer.src_mac == "00:11:22:33:44:55"
        assert layer.ethertype == 0x0800
        assert len(layer.raw) == 14


class TestIPv4:
    """Test IPv4 layer."""
    
    def test_ipv4_builder(self):
        """Test IPv4 builder."""
        builder = IPv4Builder()
        header = builder.build_header(
            src="192.168.1.1",
            dst="192.168.1.2",
            ttl=64,
            protocol=6
        )
        
        assert len(header) == 20
        # Protocol field at offset 9
        assert header[9] == 6
    
    def test_ipv4_layer(self):
        """Test IPv4 layer."""
        layer = IPv4Layer(
            src_ip="192.168.1.1",
            dst_ip="192.168.1.2",
            ttl=64,
            protocol=6
        )
        
        assert layer.src_ip == "192.168.1.1"
        assert layer.dst_ip == "192.168.1.2"
        assert len(layer.raw) == 20


class TestTCP:
    """Test TCP layer."""
    
    def test_tcp_builder(self):
        """Test TCP builder."""
        builder = TCPBuilder()
        header = builder.build_header(
            src_port=12345,
            dst_port=80,
            flags=0x02,
        )
        
        assert len(header) == 20
        # Ports at offset 0 and 2
        src_port, dst_port = header[:2], header[2:4]
        assert len(src_port) == 2
    
    def test_tcp_layer(self):
        """Test TCP layer."""
        layer = TCPLayer(
            src_port=12345,
            dst_port=80,
            flags=0x02,
        )
        
        assert layer.src_port == 12345
        assert layer.dst_port == 80
        assert len(layer.raw) == 20


class TestUDP:
    """Test UDP layer."""
    
    def test_udp_builder(self):
        """Test UDP builder."""
        builder = UDPBuilder()
        header = builder.build_header(
            src_port=12345,
            dst_port=53,
        )
        
        assert len(header) == 8
    
    def test_udp_layer(self):
        """Test UDP layer."""
        layer = UDPLayer(
            src_port=12345,
            dst_port=53,
        )
        
        assert layer.src_port == 12345
        assert layer.dst_port == 53
        assert len(layer.raw) == 8


class TestARP:
    """Test ARP layer."""
    
    def test_arp_builder(self):
        """Test ARP builder."""
        builder = ARPBuilder()
        header = builder.build_header(
            opcode=1,
            src_mac="00:11:22:33:44:55",
            src_ip="192.168.1.1",
            dst_mac="00:00:00:00:00:00",
            dst_ip="192.168.1.2",
        )
        
        assert len(header) == 28  # ARP header is 28 bytes
    
    def test_arp_layer(self):
        """Test ARP layer."""
        layer = ARPLayer(
            opcode=1,
            src_mac="00:11:22:33:44:55",
            src_ip="192.168.1.1",
        )
        
        assert layer.opcode == 1
        assert layer.src_mac == "00:11:22:33:44:55"
        assert len(layer.raw) == 28
