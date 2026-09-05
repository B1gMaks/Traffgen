from typing import List, Dict, Any, Optional
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import numpy as np
from datetime import datetime
from ..core.types import PacketData
from ..common.logger import get_logger


class ChartGenerator:
    """Generate charts from packet data."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def generate_protocol_pie_chart(
        self,
        packets: List[PacketData],
        output_path: Optional[Path] = None,
        **kwargs
    ) -> Optional[plt.Figure]:
        """Generate protocol distribution pie chart."""
        if not packets:
            self.logger.warning("No packets to visualize")
            return None
        
        # Count protocols
        protocol_counts = {}
        for packet in packets:
            proto = packet.protocol.value
            protocol_counts[proto] = protocol_counts.get(proto, 0) + 1
        
        # Sort by count
        sorted_protocols = sorted(protocol_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Take top 10, group others
        if len(sorted_protocols) > 10:
            top = sorted_protocols[:10]
            others_count = sum(count for _, count in sorted_protocols[10:])
            top.append(("Other", others_count))
            sorted_protocols = top
        
        labels = [f"{proto}\n({count})" for proto, count in sorted_protocols]
        sizes = [count for _, count in sorted_protocols]
        colors = plt.cm.tab20(np.linspace(0, 1, len(sorted_protocols)))
        
        fig, ax = plt.subplots(figsize=(10, 8))
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10},
        )
        
        ax.set_title('Protocol Distribution', fontsize=16, fontweight='bold')
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved pie chart to {output_path}")
        
        return fig
    
    def generate_packet_size_histogram(
        self,
        packets: List[PacketData],
        output_path: Optional[Path] = None,
        bins: int = 30,
        **kwargs
    ) -> Optional[plt.Figure]:
        """Generate packet size histogram."""
        if not packets:
            self.logger.warning("No packets to visualize")
            return None
        
        sizes = [p.length for p in packets]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        n, bins_edges, patches = ax.hist(
            sizes,
            bins=bins,
            color='steelblue',
            edgecolor='black',
            alpha=0.7,
        )
        
        ax.set_xlabel('Packet Size (bytes)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Packet Size Distribution', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        mean_size = np.mean(sizes)
        median_size = np.median(sizes)
        ax.axvline(mean_size, color='red', linestyle='--', label=f'Mean: {mean_size:.0f}')
        ax.axvline(median_size, color='green', linestyle='--', label=f'Median: {median_size:.0f}')
        ax.legend()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved histogram to {output_path}")
        
        return fig
    
    def generate_timeline_chart(
        self,
        packets: List[PacketData],
        output_path: Optional[Path] = None,
        bin_size: int = 1,
        **kwargs
    ) -> Optional[plt.Figure]:
        """Generate timeline chart."""
        if not packets:
            self.logger.warning("No packets to visualize")
            return None
        
        # Sort packets by timestamp
        sorted_packets = sorted(packets, key=lambda p: p.timestamp)
        start_time = sorted_packets[0].timestamp
        end_time = sorted_packets[-1].timestamp
        duration = (end_time - start_time).total_seconds()
        
        if duration == 0:
            self.logger.warning("Duration is 0, cannot generate timeline")
            return None
        
        # Create bins
        num_bins = max(1, int(duration / bin_size))
        timeline = [0] * (num_bins + 1)
        
        for packet in sorted_packets:
            offset = (packet.timestamp - start_time).total_seconds()
            bin_index = min(int(offset / bin_size), num_bins)
            timeline[bin_index] += 1
        
        fig, ax = plt.subplots(figsize=(12, 6))
        x_values = np.arange(0, duration + bin_size, bin_size)
        
        # Ensure x_values and timeline have same length
        x_values = x_values[:len(timeline)]
        
        ax.bar(x_values, timeline, width=bin_size * 0.9, color='steelblue', alpha=0.7)
        ax.set_xlabel('Time (seconds)', fontsize=12)
        ax.set_ylabel('Packets', fontsize=12)
        ax.set_title('Packet Timeline', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved timeline to {output_path}")
        
        return fig
    
    def generate_top_talkers_bar_chart(
        self,
        packets: List[PacketData],
        output_path: Optional[Path] = None,
        limit: int = 10,
        **kwargs
    ) -> Optional[plt.Figure]:
        """Generate top talkers bar chart."""
        if not packets:
            self.logger.warning("No packets to visualize")
            return None
        
        # Count bytes per address
        talkers = {}
        for packet in packets:
            src = packet.source.ipv4 or packet.source.mac or "unknown"
            talkers[src] = talkers.get(src, 0) + packet.length
        
        sorted_talkers = sorted(talkers.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        addresses = [addr[:20] for addr, _ in sorted_talkers]  # Truncate long addresses
        bytes_counts = [count for _, count in sorted_talkers]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        y_pos = np.arange(len(addresses))
        
        bars = ax.barh(y_pos, bytes_counts, color=plt.cm.viridis(np.linspace(0.2, 0.8, len(addresses))))
        ax.set_yticks(y_pos)
        ax.set_yticklabels(addresses, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel('Bytes', fontsize=12)
        ax.set_title('Top Talkers by Traffic Volume', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (bar, count) in enumerate(zip(bars, bytes_counts)):
            ax.text(count, i, f' {count:,}', va='center', fontsize=9)
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved top talkers chart to {output_path}")
        
        return fig
    
    def generate_traffic_heatmap(
        self,
        packets: List[PacketData],
        output_path: Optional[Path] = None,
        **kwargs
    ) -> Optional[plt.Figure]:
        """Generate traffic heatmap (time vs protocol)."""
        if not packets:
            self.logger.warning("No packets to visualize")
            return None
        
        # Group by time (hour) and protocol
        hours = [p.timestamp.hour for p in packets]
        protocols = [p.protocol.value for p in packets]
        
        unique_protocols = list(set(protocols))
        unique_hours = sorted(set(hours))
        
        # Create matrix
        matrix = np.zeros((len(unique_hours), len(unique_protocols)))
        for hour, proto in zip(hours, protocols):
            hour_idx = unique_hours.index(hour)
            proto_idx = unique_protocols.index(proto)
            matrix[hour_idx, proto_idx] += 1
        
        fig, ax = plt.subplots(figsize=(12, 8))
        im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto', interpolation='nearest')
        
        ax.set_xticks(np.arange(len(unique_protocols)))
        ax.set_yticks(np.arange(len(unique_hours)))
        ax.set_xticklabels([p[:10] for p in unique_protocols], rotation=45, ha='right', fontsize=8)
        ax.set_yticklabels(unique_hours)
        
        ax.set_xlabel('Protocol', fontsize=12)
        ax.set_ylabel('Hour', fontsize=12)
        ax.set_title('Traffic Heatmap (Hour vs Protocol)', fontsize=14, fontweight='bold')
        
        plt.colorbar(im, ax=ax, label='Packet Count')
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved heatmap to {output_path}")
        
        return fig
    
    def generate_comprehensive_report(
        self,
        packets: List[PacketData],
        output_dir: Path,
        **kwargs
    ) -> List[Path]:
        """Generate all charts in a directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        outputs = []
        
        # Generate all charts
        charts = [
            (self.generate_protocol_pie_chart, "protocol_pie.png"),
            (self.generate_packet_size_histogram, "packet_size_hist.png"),
            (self.generate_timeline_chart, "timeline.png"),
            (self.generate_top_talkers_bar_chart, "top_talkers.png"),
            (self.generate_traffic_heatmap, "traffic_heatmap.png"),
        ]
        
        for chart_func, filename in charts:
            output_path = output_dir / filename
            fig = chart_func(packets, output_path, **kwargs)
            if fig:
                plt.close(fig)
                outputs.append(output_path)
        
        return outputs
