from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime, timedelta
from ..core.types import PacketData, FlowData, ProtocolType
from .protocols import ProtocolAnalyzer
from .flows import FlowAnalyzer
from .conversations import ConversationAnalyzer
from ..common.logger import get_logger


class Analyzer:
    """Main analysis engine."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.protocol_analyzer = ProtocolAnalyzer()
        self.flow_analyzer = FlowAnalyzer()
        self.conversation_analyzer = ConversationAnalyzer()
    
    def analyze(self, packets: List[PacketData]) -> Dict[str, Any]:
        """Perform comprehensive analysis."""
        self.logger.info(f"Analyzing {len(packets)} packets")
        
        if not packets:
            return {"error": "No packets to analyze"}
        
        results = {
            "summary": self._get_summary(packets),
            "protocols": self.protocol_analyzer.analyze(packets),
            "flows": self.flow_analyzer.analyze(packets),
            "conversations": self.conversation_analyzer.analyze(packets),
            "timeline": self._get_timeline(packets),
            "top_talkers": self._get_top_talkers(packets),
            "packet_size": self._get_packet_size_stats(packets),
            "bandwidth": self._get_bandwidth_stats(packets),
        }
        
        self.logger.info("Analysis complete")
        return results
    
    def _get_summary(self, packets: List[PacketData]) -> Dict[str, Any]:
        """Get basic summary."""
        total_bytes = sum(p.length for p in packets)
        start_time = min(p.timestamp for p in packets)
        end_time = max(p.timestamp for p in packets)
        duration = (end_time - start_time).total_seconds()
        
        return {
            "total_packets": len(packets),
            "total_bytes": total_bytes,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "average_packet_size": total_bytes / len(packets) if packets else 0,
            "packets_per_second": len(packets) / duration if duration > 0 else 0,
            "bytes_per_second": total_bytes / duration if duration > 0 else 0,
        }
    
    def _get_timeline(self, packets: List[PacketData]) -> Dict[str, Any]:
        """Get timeline statistics."""
        if not packets:
            return {}
        
        start_time = min(p.timestamp for p in packets)
        end_time = max(p.timestamp for p in packets)
        duration = (end_time - start_time).total_seconds()
        
        # Create bins (1 second intervals)
        bin_size = max(1, duration / 60)  # Max 60 bins
        bins = {}
        
        for packet in packets:
            offset = (packet.timestamp - start_time).total_seconds()
            bin_key = int(offset / bin_size)
            bins[bin_key] = bins.get(bin_key, 0) + 1
        
        return {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration": duration,
            "bin_size": bin_size,
            "bins": bins,
        }
    
    def _get_top_talkers(self, packets: List[PacketData], limit: int = 10) -> List[Dict[str, Any]]:
        """Get top talkers by traffic volume."""
        talkers = defaultdict(int)
        
        for packet in packets:
            src = packet.source.ipv4 or packet.source.mac or "unknown"
            talkers[src] += packet.length
        
        sorted_talkers = sorted(talkers.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                "address": addr,
                "bytes": bytes_count,
                "percentage": (bytes_count / sum(talkers.values())) * 100 if talkers else 0,
            }
            for addr, bytes_count in sorted_talkers[:limit]
        ]
    
    def _get_packet_size_stats(self, packets: List[PacketData]) -> Dict[str, Any]:
        """Get packet size statistics."""
        if not packets:
            return {}
        
        sizes = [p.length for p in packets]
        
        return {
            "min": min(sizes),
            "max": max(sizes),
            "mean": sum(sizes) / len(sizes),
            "median": sorted(sizes)[len(sizes) // 2],
            "std_dev": self._calculate_std_dev(sizes),
        }
    
    def _get_bandwidth_stats(self, packets: List[PacketData]) -> Dict[str, Any]:
        """Get bandwidth statistics."""
        if not packets:
            return {}
        
        total_bytes = sum(p.length for p in packets)
        start_time = min(p.timestamp for p in packets)
        end_time = max(p.timestamp for p in packets)
        duration = (end_time - start_time).total_seconds()
        
        # Bandwidth per second
        bandwidth = {}
        for packet in packets:
            second = int(packet.timestamp.timestamp())
            bandwidth[second] = bandwidth.get(second, 0) + packet.length
        
        return {
            "total_bytes": total_bytes,
            "duration_seconds": duration,
            "average_bps": total_bytes / duration if duration > 0 else 0,
            "peak_bps": max(bandwidth.values()) if bandwidth else 0,
            "bandwidth_per_second": bandwidth,
        }
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
