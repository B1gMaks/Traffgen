import random
import struct
import hashlib
from typing import Optional, Tuple
from ipaddress import IPv4Address, IPv6Address


def generate_mac() -> str:
    """Generate a random MAC address."""
    mac = [0x02, 0x00, 0x00, 
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ":".join(f"{b:02x}" for b in mac)


def generate_ipv4() -> str:
    """Generate a random IPv4 address."""
    # Use private IP ranges
    ranges = [
        (10, 0, 0, 0, 10, 255, 255, 255),
        (172, 16, 0, 0, 172, 31, 255, 255),
        (192, 168, 0, 0, 192, 168, 255, 255),
    ]
    range_choice = random.choice(ranges)
    a1, b1, c1, d1, a2, b2, c2, d2 = range_choice
    
    return f"{random.randint(a1, a2)}.{random.randint(b1, b2)}.{random.randint(c1, c2)}.{random.randint(d1, d2)}"


def generate_ipv6() -> str:
    """Generate a random IPv6 address."""
    parts = []
    for _ in range(8):
        parts.append(f"{random.randint(0, 0xffff):04x}")
    return ":".join(parts)


def generate_port() -> int:
    """Generate a random port number."""
    # Ephemeral ports
    return random.randint(49152, 65535)


def generate_well_known_port(protocol: str) -> int:
    """Generate a well-known port for a protocol."""
    ports = {
        "dns": 53,
        "http": 80,
        "https": 443,
        "smtp": 25,
        "pop3": 110,
        "imap": 143,
        "ftp": 21,
        "ssh": 22,
        "telnet": 23,
        "ntp": 123,
        "dhcp": 67,
        "snmp": 161,
        "mqtt": 1883,
        "sip": 5060,
        "rtp": 5004,
        "syslog": 514,
    }
    return ports.get(protocol.lower(), generate_port())


def calculate_checksum(data: bytes) -> int:
    """Calculate IP checksum."""
    if len(data) % 2 == 1:
        data += b'\x00'
    
    checksum = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]
        checksum += word
        checksum = (checksum & 0xffff) + (checksum >> 16)
    
    return ~checksum & 0xffff


def bytes_to_hex(data: bytes, separator: str = " ") -> str:
    """Convert bytes to hex string."""
    return separator.join(f"{b:02x}" for b in data)


def hex_to_bytes(hex_str: str) -> bytes:
    """Convert hex string to bytes."""
    hex_str = hex_str.replace(" ", "").replace(":", "")
    return bytes.fromhex(hex_str)


def calculate_hash(data: bytes) -> str:
    """Calculate SHA256 hash of data."""
    return hashlib.sha256(data).hexdigest()


def truncate_string(s: str, max_len: int = 100) -> str:
    """Truncate string to max length."""
    if len(s) <= max_len:
        return s
    return s[:max_len] + "..."


def generate_random_bytes(length: int) -> bytes:
    """Generate random bytes."""
    return bytes(random.randint(0, 255) for _ in range(length))


def generate_payload_with_pattern(length: int, pattern: bytes = b"ABCD") -> bytes:
    """Generate payload with repeating pattern."""
    return (pattern * ((length // len(pattern)) + 1))[:length]


def get_timestamp_microseconds() -> int:
    """Get current timestamp in microseconds."""
    import time
    return int(time.time() * 1_000_000)


def format_bytes(bytes_count: int) -> str:
    """Format bytes to human readable."""
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    for unit in units:
        if bytes_count < 1024:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024
    return f"{bytes_count:.2f} PB"


def parse_time_string(time_str: str) -> int:
    """Parse time string (e.g., "1h", "30m", "3600s") to seconds."""
    if time_str.endswith('h'):
        return int(time_str[:-1]) * 3600
    elif time_str.endswith('m'):
        return int(time_str[:-1]) * 60
    elif time_str.endswith('s'):
        return int(time_str[:-1])
    else:
        return int(time_str)
