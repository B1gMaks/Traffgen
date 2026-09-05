from .base import Profile, Host, HostType, Service, TrafficPattern
from ..core.types import ProtocolType


class EnterpriseProfile(Profile):
    """Enterprise network profile."""
    
    def __init__(self):
        super().__init__(
            name="enterprise",
            description="Large enterprise network with multiple departments and services",
        )
        
        # Define subnets
        self.subnets = [
            "10.0.0.0/24",   # Management
            "10.0.1.0/24",   # Engineering
            "10.0.2.0/24",   # Sales
            "10.0.3.0/24",   # Marketing
            "10.0.10.0/24",  # Servers
            "10.0.20.0/24",  # DMZ
            "10.0.30.0/24",  # IoT
        ]
        
        # Define hosts
        self.hosts = [
            Host(
                name="engineering-clients",
                host_type=HostType.CLIENT,
                ip_range="10.0.1.0/24",
                count=100,
                services=["ssh", "http", "https", "dns", "ntp"],
                os="Ubuntu",
                version="22.04",
                tags=["engineering", "development"],
            ),
            Host(
                name="sales-clients",
                host_type=HostType.CLIENT,
                ip_range="10.0.2.0/24",
                count=50,
                services=["http", "https", "dns", "ntp", "smtp"],
                os="Windows 11",
                version="22H2",
                tags=["sales", "office"],
            ),
            Host(
                name="marketing-clients",
                host_type=HostType.CLIENT,
                ip_range="10.0.3.0/24",
                count=30,
                services=["http", "https", "dns", "ntp"],
                os="macOS",
                version="14.0",
                tags=["marketing", "design"],
            ),
            Host(
                name="web-servers",
                host_type=HostType.WEB,
                ip_range="10.0.10.0/24",
                count=5,
                services=["http", "https", "dns"],
                os="Ubuntu",
                version="22.04",
                tags=["production", "web"],
            ),
            Host(
                name="database-servers",
                host_type=HostType.DATABASE,
                ip_range="10.0.10.0/24",
                count=3,
                services=["mysql", "postgresql", "redis"],
                os="Ubuntu",
                version="22.04",
                tags=["production", "database"],
            ),
            Host(
                name="mail-servers",
                host_type=HostType.MAIL,
                ip_range="10.0.10.0/24",
                count=2,
                services=["smtp", "pop3", "imap"],
                os="Ubuntu",
                version="22.04",
                tags=["production", "mail"],
            ),
            Host(
                name="dns-servers",
                host_type=HostType.DNS,
                ip_range="10.0.0.0/24",
                count=2,
                services=["dns"],
                os="Ubuntu",
                version="22.04",
                tags=["infrastructure", "dns"],
            ),
            Host(
                name="dhcp-servers",
                host_type=HostType.DHCP,
                ip_range="10.0.0.0/24",
                count=1,
                services=["dhcp"],
                os="Ubuntu",
                version="22.04",
                tags=["infrastructure", "dhcp"],
            ),
            Host(
                name="iot-devices",
                host_type=HostType.IOT,
                ip_range="10.0.30.0/24",
                count=20,
                services=["mqtt", "coap"],
                os="IoT OS",
                version="1.0",
                tags=["iot", "sensors"],
            ),
            Host(
                name="printers",
                host_type=HostType.PRINTER,
                ip_range="10.0.0.0/24",
                count=5,
                services=["ipp", "snmp"],
                os="Printer OS",
                version="1.0",
                tags=["office", "printers"],
            ),
        ]
        
        # Define services
        self.services = [
            Service("http", ProtocolType.HTTP, 80, "1.1", False, "Web traffic"),
            Service("https", ProtocolType.HTTPS, 443, "1.1", True, "Secure web traffic"),
            Service("dns", ProtocolType.DNS, 53, "1.0", False, "DNS resolution"),
            Service("dhcp", ProtocolType.DHCP, 67, "1.0", False, "DHCP lease"),
            Service("smtp", ProtocolType.SMTP, 25, "1.0", False, "Email submission"),
            Service("pop3", ProtocolType.POP3, 110, "1.0", False, "Email retrieval"),
            Service("imap", ProtocolType.IMAP, 143, "1.0", False, "Email synchronization"),
            Service("mqtt", ProtocolType.MQTT, 1883, "5.0", False, "IoT messaging"),
            Service("coap", ProtocolType.COAP, 5683, "1.0", False, "IoT discovery"),
            Service("ntp", ProtocolType.NTP, 123, "4.0", False, "Time synchronization"),
            Service("snmp", ProtocolType.SNMP, 161, "3.0", False, "Network monitoring"),
            Service("ssh", ProtocolType.SSH, 22, "2.0", True, "Secure shell"),
        ]
        
        # Define traffic patterns
        self.traffic_patterns = [
            TrafficPattern("web-browsing", ProtocolType.HTTP, 30, 1024, 50.0, 0.2, 8, "poisson"),
            TrafficPattern("secure-web", ProtocolType.HTTPS, 25, 2048, 30.0, 0.3, 12, "poisson"),
            TrafficPattern("dns-queries", ProtocolType.DNS, 15, 256, 20.0, 0.0, 2, "poisson"),
            TrafficPattern("email-smtp", ProtocolType.SMTP, 5, 4096, 5.0, 0.1, 5, "uniform"),
            TrafficPattern("email-pop3", ProtocolType.POP3, 3, 8192, 3.0, 0.0, 3, "uniform"),
            TrafficPattern("email-imap", ProtocolType.IMAP, 3, 4096, 3.0, 0.0, 4, "uniform"),
            TrafficPattern("iot-mqtt", ProtocolType.MQTT, 8, 128, 15.0, 0.5, 3, "poisson"),
            TrafficPattern("iot-coap", ProtocolType.COAP, 4, 256, 8.0, 0.2, 2, "poisson"),
            TrafficPattern("ntp-sync", ProtocolType.NTP, 4, 128, 2.0, 0.0, 1, "fixed"),
            TrafficPattern("snmp-polling", ProtocolType.SNMP, 3, 512, 5.0, 0.0, 2, "fixed"),
            TrafficPattern("dhcp-lease", ProtocolType.DHCP, 2, 512, 1.0, 0.0, 4, "uniform"),
            TrafficPattern("tls-handshake", ProtocolType.TLS, 8, 2048, 10.0, 0.0, 6, "poisson"),
        ]
