import pytest
from trafficlab.protocols.dns import generate_dns_query, generate_dns_response
from trafficlab.protocols.dhcp import (
    generate_dhcp_discover,
    generate_dhcp_offer,
    generate_dhcp_request,
    generate_dhcp_ack,
)
from trafficlab.protocols.tls import generate_tls_client_hello, generate_tls_server_hello


class TestDNS:
    """Test DNS protocol."""
    
    def test_dns_query(self):
        """Test DNS query generation."""
        query = generate_dns_query()
        assert len(query) > 0
        # DNS header is 12 bytes
        assert len(query) >= 12
    
    def test_dns_response(self):
        """Test DNS response generation."""
        response = generate_dns_response()
        assert len(response) > 0
        assert len(response) >= 12


class TestDHCP:
    """Test DHCP protocol."""
    
    def test_dhcp_discover(self):
        """Test DHCP Discover generation."""
        discover = generate_dhcp_discover()
        assert len(discover) > 0
    
    def test_dhcp_offer(self):
        """Test DHCP Offer generation."""
        offer = generate_dhcp_offer()
        assert len(offer) > 0
    
    def test_dhcp_request(self):
        """Test DHCP Request generation."""
        request = generate_dhcp_request()
        assert len(request) > 0
    
    def test_dhcp_ack(self):
        """Test DHCP ACK generation."""
        ack = generate_dhcp_ack()
        assert len(ack) > 0


class TestTLS:
    """Test TLS protocol."""
    
    def test_tls_client_hello(self):
        """Test TLS Client Hello generation."""
        hello = generate_tls_client_hello()
        assert len(hello) > 0
        # TLS handshake header is 4 bytes + handshake header
        assert len(hello) >= 4
    
    def test_tls_server_hello(self):
        """Test TLS Server Hello generation."""
        hello = generate_tls_server_hello()
        assert len(hello) > 0
        assert len(hello) >= 4
