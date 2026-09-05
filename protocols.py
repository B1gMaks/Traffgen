from typing import List, Dict, Any, Set
from collections import defaultdict
from ..core.types import PacketData, ProtocolType


class ProtocolAnalyzer:
    """Analyze protocol distribution."""
    
    def analyze(self, packets: List[PacketData]) -> Dict[str, Any]:
        """Analyze protocol distribution."""
        if not packets:
            return {}
        
        counts = defaultdict(int)
        bytes_by_protocol = defaultdict(int)
        
        for packet in packets:
            proto = packet.protocol.value
            counts[proto] += 1
            bytes_by_protocol[proto] += packet.length
        
        total_packets = len(packets)
        total_bytes = sum(p.length for p in packets)
        
        result = {
            "protocols": [],
            "total_packets": total_packets,
            "total_bytes": total_bytes,
        }
        
        for proto in sorted(set(counts.keys())):
            result["protocols"].append({
                "name": proto,
                "packets": counts[proto],
                "bytes": bytes_by_protocol[proto],
                "packet_percentage": (counts[proto] / total_packets) * 100,
                "byte_percentage": (bytes_by_protocol[proto] / total_bytes) * 100 if total_bytes > 0 else 0,
            })
        
        return result
