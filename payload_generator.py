import random
import json
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List
from datetime import datetime
from faker import Faker

fake = Faker()


class PayloadGenerator:
    """Generate realistic payloads."""
    
    def __init__(self):
        self._html_templates = [
            "<html><head><title>Welcome</title></head><body><h1>Hello World</h1><p>{text}</p></body></html>",
            "<!DOCTYPE html><html><body><h2>{title}</h2><p>{paragraph}</p><ul><li>{item1}</li><li>{item2}</li></ul></body></html>",
            "<html><body><form><input type='text' name='search'><input type='submit'></form></body></html>",
        ]
        
        self._lorem_ipsum = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
            "Duis aute irure dolor in reprehenderit in voluptate velit esse.",
            "Excepteur sint occaecat cupidatat non proident, sunt in culpa.",
        ]
    
    def generate_payload(self, size: int = 512, pattern: str = "random") -> bytes:
        """Generate generic payload."""
        if pattern == "lorem":
            return self.generate_lorem_ipsum(size).encode()
        elif pattern == "binary":
            return self.generate_binary(size)
        elif pattern == "zeros":
            return b"\x00" * size
        elif pattern == "ones":
            return b"\xff" * size
        elif pattern == "pattern":
            return self.generate_pattern(size, b"ABCD")
        else:
            return self.generate_random(size)
    
    def generate_random(self, size: int) -> bytes:
        """Generate random bytes."""
        return bytes(random.randint(0, 255) for _ in range(size))
    
    def generate_binary(self, size: int) -> bytes:
        """Generate binary payload."""
        return bytes(random.randint(0, 255) for _ in range(size))
    
    def generate_pattern(self, size: int, pattern: bytes = b"ABCD") -> bytes:
        """Generate repeating pattern."""
        return (pattern * ((size // len(pattern)) + 1))[:size]
    
    def generate_lorem_ipsum(self, size: int = 512) -> str:
        """Generate Lorem Ipsum text."""
        text = " ".join(random.choices(self._lorem_ipsum, k=size // 50 + 1))
        return text[:size]
    
    def generate_html(self) -> str:
        """Generate HTML page."""
        template = random.choice(self._html_templates)
        return template.format(
            text=fake.text(max_nb_chars=200),
            title=fake.sentence(),
            paragraph=fake.paragraph(),
            item1=fake.word(),
            item2=fake.word(),
        )
    
    def generate_json(self) -> str:
        """Generate JSON data."""
        data = {
            "id": random.randint(1, 1000),
            "name": fake.name(),
            "email": fake.email(),
            "address": fake.address(),
            "phone": fake.phone_number(),
            "timestamp": datetime.now().isoformat(),
            "data": {
                "value": random.uniform(0, 100),
                "status": random.choice(["active", "inactive", "pending"]),
                "tags": [fake.word() for _ in range(random.randint(1, 5))],
            }
        }
        return json.dumps(data, indent=2)
    
    def generate_xml(self) -> str:
        """Generate XML data."""
        root = ET.Element("root")
        
        for _ in range(random.randint(2, 5)):
            item = ET.SubElement(root, "item")
            ET.SubElement(item, "id").text = str(random.randint(1, 100))
            ET.SubElement(item, "name").text = fake.word()
            ET.SubElement(item, "value").text = str(random.uniform(0, 100))
            ET.SubElement(item, "active").text = str(random.choice([True, False]))
        
        return ET.tostring(root, encoding='unicode')
    
    def generate_csv(self, rows: int = 10) -> str:
        """Generate CSV data."""
        headers = ["id", "name", "email", "value", "status"]
        lines = [",".join(headers)]
        
        for _ in range(rows):
            row = [
                str(random.randint(1, 1000)),
                fake.name(),
                fake.email(),
                str(random.uniform(0, 100)),
                random.choice(["active", "inactive", "pending"]),
            ]
            lines.append(",".join(row))
        
        return "\n".join(lines)
    
    def generate_http_request(self, method: Optional[str] = None) -> str:
        """Generate HTTP request."""
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        method = method or random.choice(methods)
        
        paths = ["/", "/index.html", "/api/v1/users", "/api/v1/data", "/about", "/contact"]
        path = random.choice(paths)
        
        return f"{method} {path} HTTP/1.1\r\nHost: {fake.domain_name()}\r\nUser-Agent: Mozilla/5.0\r\nAccept: */*\r\n\r\n"
    
    def generate_http_response(self, status_code: int = 200) -> str:
        """Generate HTTP response."""
        status_messages = {
            200: "OK",
            201: "Created",
            301: "Moved Permanently",
            302: "Found",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            500: "Internal Server Error",
        }
        
        status_code = status_code or random.choice(list(status_messages.keys()))
        status_message = status_messages.get(status_code, "OK")
        
        body = self.generate_html() if status_code < 400 else f"<h1>{status_code} {status_message}</h1>"
        
        return f"HTTP/1.1 {status_code} {status_message}\r\nContent-Type: text/html\r\nContent-Length: {len(body)}\r\n\r\n{body}"
    
    def generate_email(self) -> str:
        """Generate email content."""
        return f"""From: {fake.email()}
To: {fake.email()}
Subject: {fake.sentence()}
Date: {datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}

{fake.paragraph()}

{fake.paragraph()}

Regards,
{fake.name()}
"""
    
    def generate_log_message(self) -> str:
        """Generate syslog message."""
        levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        level = random.choice(levels)
        
        messages = [
            "Connection established from {ip}",
            "Authentication failed for user '{user}'",
            "Database query executed in {time}ms",
            "Service started on port {port}",
            "Request processed in {time}ms",
            "Cache miss for key '{key}'",
            "Memory usage at {percent}%",
        ]
        
        template = random.choice(messages)
        msg = template.format(
            ip=fake.ipv4(),
            user=fake.user_name(),
            time=random.randint(10, 1000),
            port=random.randint(1024, 65535),
            key=fake.word(),
            percent=random.randint(10, 90),
        )
        
        return f"{datetime.now().isoformat()} [{level}] {msg}\n"
