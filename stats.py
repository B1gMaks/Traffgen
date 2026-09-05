from typing import List, Dict, Any
from collections import defaultdict
import statistics
from ..core.types import PacketData


class StatisticsEngine:
    """Compute comprehensive statistics."""
    
    def analyze(self, packets: List[PacketData]) -> Dict[str, Any]:
        """Compute statistics for packets."""
        if not packets:
            return {}
        
        return {
            "packet_stats": self._packet_stats(packets),
            "size_stats": self._size_stats(packets),
            "timing_stats": self._timing_stats(packets),
            "protocol_stats": self._protocol_stats(packets),
            "port_stats": self._port_stats(packets),
        }
    
    def _packet_stats(self, packets: List[PacketData]) -> Dict[str, Any]:
        """Compute packet statistics."""
        return {
            "count": len(packets),
            "total_bytes": sum(p.length for p in packets),
        }
    
    def _size_stats(self, packets: List[PacketData]) -> Dict[str, Any]:
        """Compute packet size statistics."""
        sizes = [p.length for p in packets]
        
        return {
            "min": min(sizes),
            "max": max(sizes),
            "mean": statistics.mean(sizes),
            "median": statistics.median(sizes),
            "std_dev": statistics.stdev(sizes) if len(sizes) > 1 else 0,
            "q1": statistics.quantiles(sizes, n=4)[0] if len(sizes) >= 4 else 0,
            "q3": statistics.quantiles(sizes, n=4)[2] if len(sizes) >= 4 else 0,
        }
    
    def _timing_stats(self, packets: List[PacketData]) -> Dict[str, Any]:
        """Compute timing statistics."""
        if len(packets) < 2:
            return {}
        
        timestamps = [p.timestamp.timestamp() for p in packets]
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps) - 1)]
        
        return {
            "duration": timestamps[-1] - timestamps[0],
            "min_interval": min(intervals),
            "max_interval": max(intervals),
            "mean_interval": statistics.mean(intervals),
            "std_interval": statistics.stdev(intervals) if len(intervals) > 1 else 0,
            "packets_per_second": len(packets) / (timestamps[-1] - timestamps[0]) if timestamps[-1] > timestamps[0] else 0,
        }
    
    def _protocol_stats(self, packets: List[PacketData]) -> Dict[str, Any]:
        """Compute protocol statistics."""
        counts = defaultdict(int)
        bytes_by_protocol = defaultdict(int)
        
        for packet in packets:
            proto = packet.protocol.value
            counts[proto] += 1
            bytes_by_protocol[proto] += packet.length
        
        return {
            "distribution": dict(counts),
            "bytes_by_protocol": dict(bytes_by_protocol),
            "unique_protocols": len(counts),
        }
    
    def _port_stats(self, packets: List[PacketData]) -> Dict[str, Any]:
        """Compute port statistics."""
        src_ports = defaultdict(int)
        dst_ports = defaultdict(int)
        
        for packet in packets:
            if packet.source.port:
                src_ports[packet.source.port] += 1
            if packet.destination.port:
                dst_ports[packet.destination.port] += 1
        
        return {
            "source_ports": dict(sorted(src_ports.items(), key=lambda x: x[1], reverse=True)[:10]),
            "destination_ports": dict(sorted(dst_ports.items(), key=lambda x: x[1], reverse=True)[:10]),
        }
