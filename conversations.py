from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict
from ..core.types import PacketData, Address


class ConversationAnalyzer:
    """Analyze conversations between hosts."""
    
    def analyze(self, packets: List[PacketData]) -> Dict[str, Any]:
        """Analyze conversations."""
        if not packets:
            return {}
        
        conversations = self._extract_conversations(packets)
        
        return {
            "total_conversations": len(conversations),
            "conversations": [
                {
                    "src": self._address_to_dict(conv[0]),
                    "dst": self._address_to_dict(conv[1]),
                    "packets": count,
                    "bytes": bytes_count,
                }
                for conv, (count, bytes_count) in sorted(
                    conversations.items(),
                    key=lambda x: x[1][0],
                    reverse=True
                )[:20]
            ],
        }
    
    def _extract_conversations(self, packets: List[PacketData]) -> Dict[Tuple[Address, Address], Tuple[int, int]]:
        """Extract conversations from packets."""
        conversations = defaultdict(lambda: (0, 0))
        
        for packet in packets:
            key = (packet.source, packet.destination)
            count, bytes_count = conversations[key]
            conversations[key] = (count + 1, bytes_count + packet.length)
        
        return conversations
    
    def _address_to_dict(self, addr: Address) -> Dict[str, Any]:
        """Convert address to dictionary."""
        return {
            "mac": addr.mac,
            "ipv4": addr.ipv4,
            "ipv6": addr.ipv6,
            "port": addr.port,
            "hostname": addr.hostname,
        }
