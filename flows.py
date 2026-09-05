from typing import List, Dict, Any, Optional
from collections import defaultdict
from ..core.types import PacketData, FlowData, Address
from ..common.utils import generate_ipv4


class FlowAnalyzer:
    """Analyze network flows."""
    
    def analyze(self, packets: List[PacketData]) -> Dict[str, Any]:
        """Analyze flows."""
        if not packets:
            return {}
        
        flows = self._extract_flows(packets)
        
        return {
            "total_flows": len(flows),
            "flows": [
                {
                    "id": flow.flow_id,
                    "source": self._address_to_dict(flow.source),
                    "destination": self._address_to_dict(flow.destination),
                    "protocol": flow.protocol.value,
                    "packets": flow.packet_count,
                    "bytes": flow.byte_count,
                    "duration": flow.duration,
                    "packets_per_second": flow.packet_count / flow.duration if flow.duration > 0 else 0,
                }
                for flow in flows[:20]  # Top 20 flows
            ],
        }
    
    def _extract_flows(self, packets: List[PacketData]) -> List[FlowData]:
        """Extract flows from packets."""
        flows_dict = {}
        
        for packet in packets:
            # Create flow key
            src = packet.source
            dst = packet.destination
            key = f"{src.ipv4 or src.mac}:{src.port}->{dst.ipv4 or dst.mac}:{dst.port}:{packet.protocol.value}"
            
            if key not in flows_dict:
                flows_dict[key] = FlowData(
                    flow_id=key,
                    source=src,
                    destination=dst,
                    protocol=packet.protocol,
                    start_time=packet.timestamp,
                )
            
            flows_dict[key].add_packet(packet)
        
        return sorted(flows_dict.values(), key=lambda f: f.packet_count, reverse=True)
    
    def _address_to_dict(self, addr: Address) -> Dict[str, Any]:
        """Convert address to dictionary."""
        return {
            "mac": addr.mac,
            "ipv4": addr.ipv4,
            "ipv6": addr.ipv6,
            "port": addr.port,
            "hostname": addr.hostname,
        }
