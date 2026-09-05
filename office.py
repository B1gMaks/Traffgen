from .base import Profile, Host, HostType, Service, TrafficPattern
from ..core.types import ProtocolType


class OfficeProfile(Profile):
    """Office network profile."""
    
    def __init__(self):
        super().__init__(
            name="office",
            description="Small to medium office network",
        )
        
        self.subnets = [
            "192.168.1.0/24",  # Main
            "192.168.10.0/24", # Servers
            "192.168.20.0/24", # WiFi
        ]
        
        self.hosts = [
            Host(
                name="workstations",
                host_type=HostType.CLIENT,
                ip_range="192.168.1.0/24",
                count=25,
                services=["http", "https", "dns", "ntp", "smtp"],
                os="Windows 10",
                version="22H2",
                tags=["office", "workstations"],
            ),
            Host(
                name="laptops",
                host_type=HostType.CLIENT,
                ip_range="192.168.20.0/24",
                count=15,
                services=["http", "https", "dns", "ntp"],
                os="macOS",
                version="14.0",
                tags=["office", "laptops", "wifi"],
            ),
            Host(
                name="file-server",
                host_type=HostType.SERVER,
                ip_range="192.168.10.0/24",
                count=1,
                services=["smb", "http", "https"],
                os="Windows Server",
                version="2022",
                tags=["office", "fileserver"],
            ),
            Host(
                name="printers",
                host_type=HostType.PRINTER,
                ip_range="192.168.1.0/24",
                count=2,
                services=["ipp", "snmp"],
                os="Printer OS",
                version="1.0",
                tags=["office", "printers"],
            ),
            Host(
                name="dns-server",
                host_type=HostType.DNS,
                ip_range="192.168.10.0/24",
                count=1,
                services=["dns"],
                os="Ubuntu",
                version="22.04",
                tags=["office", "dns"],
            ),
        ]
        
        self.services = [
            Service("http", ProtocolType.HTTP, 80, "1.1", False, "Web traffic"),
            Service("https", ProtocolType.HTTPS, 443, "1.1", True, "Secure web"),
            Service("dns", ProtocolType.DNS, 53, "1.0", False, "DNS"),
            Service("ntp", ProtocolType.NTP, 123, "4.0", False, "NTP"),
            Service("smtp", ProtocolType.SMTP, 25, "1.0", False, "Email"),
            Service("snmp", ProtocolType.SNMP, 161, "3.0", False, "Monitoring"),
            Service("smb", ProtocolType.SMB, 445, "3.1", False, "File sharing"),
        ]
        
        self.traffic_patterns = [
            TrafficPattern("web-browsing", ProtocolType.HTTP, 35, 1024, 40.0, 0.2, 10, "poisson"),
            TrafficPattern("secure-web", ProtocolType.HTTPS, 30, 2048, 25.0, 0.3, 15, "poisson"),
            TrafficPattern("dns", ProtocolType.DNS, 15, 256, 15.0, 0.0, 2, "poisson"),
            TrafficPattern("ntp", ProtocolType.NTP, 5, 128, 2.0, 0.0, 1, "fixed"),
            TrafficPattern("email", ProtocolType.SMTP, 5, 4096, 3.0, 0.1, 4, "uniform"),
            TrafficPattern("file-sharing", ProtocolType.SMB, 5, 8192, 5.0, 0.5, 8, "burst"),
            TrafficPattern("snmp", ProtocolType.SNMP, 5, 512, 3.0, 0.0, 2, "fixed"),
        ]
