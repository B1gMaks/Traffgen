from typing import List, Dict, Any, Tuple
import math
from ..core.types import PacketData


class HistogramGenerator:
    """Generate histograms from packet data."""
    
    def generate_packet_size_histogram(self, packets: List[PacketData], bins: int = 20) -> Dict[str, Any]:
        """Generate packet size histogram."""
        if not packets:
            return {}
        
        sizes = [p.length for p in packets]
        min_size = min(sizes)
        max_size = max(sizes)
        bin_width = (max_size - min_size) / bins
        
        hist = {}
        for i in range(bins):
            low = min_size + i * bin_width
            high = low + bin_width
            count = sum(1 for s in sizes if low <= s < high)
            hist[f"{low:.0f}-{high:.0f}"] = count
        
        # Handle max value
        max_count = sum(1 for s in sizes if s == max_size)
        if max_count > 0:
            hist[f"{max_size:.0f}"] = max_count
        
        return {
            "min": min_size,
            "max": max_size,
            "bin_width": bin_width,
            "histogram": hist,
        }
    
    def generate_timeline_histogram(
        self,
        packets: List[PacketData],
        bin_size_seconds: int = 1
    ) -> Dict[str, Any]:
        """Generate timeline histogram."""
        if not packets:
            return {}
        
        start_time = min(p.timestamp for p in packets)
        end_time = max(p.timestamp for p in packets)
        duration = (end_time - start_time).total_seconds()
        
        num_bins = math.ceil(duration / bin_size_seconds)
        hist = [0] * num_bins
        
        for packet in packets:
            offset = (packet.timestamp - start_time).total_seconds()
            bin_index = min(int(offset / bin_size_seconds), num_bins - 1)
            hist[bin_index] += 1
        
        return {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "bin_size_seconds": bin_size_seconds,
            "num_bins": num_bins,
            "histogram": hist,
        }
