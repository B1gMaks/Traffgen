import re
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Union


def validate_ipv4(ip: str) -> bool:
    """Validate IPv4 address."""
    try:
        IPv4Address(ip)
        return True
    except ValueError:
        return False


def validate_ipv6(ip: str) -> bool:
    """Validate IPv6 address."""
    try:
        IPv6Address(ip)
        return True
    except ValueError:
        return False


def validate_ip(ip: str) -> bool:
    """Validate IPv4 or IPv6 address."""
    try:
        ip_address(ip)
        return True
    except ValueError:
        return False


def validate_mac(mac: str) -> bool:
    """Validate MAC address."""
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac))


def validate_port(port: int) -> bool:
    """Validate port number."""
    return 0 <= port <= 65535


def validate_hostname(hostname: str) -> bool:
    """Validate hostname."""
    if len(hostname) > 253:
        return False
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    return bool(re.match(pattern, hostname))


def validate_domain(domain: str) -> bool:
    """Validate domain name."""
    return validate_hostname(domain)


def validate_email(email: str) -> bool:
    """Validate email address."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_protocol_name(name: str) -> bool:
    """Validate protocol name."""
    return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name))


def validate_vlan_id(vlan_id: int) -> bool:
    """Validate VLAN ID."""
    return 0 <= vlan_id <= 4095


def validate_ttl(ttl: int) -> bool:
    """Validate TTL value."""
    return 0 <= ttl <= 255
