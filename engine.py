from typing import List, Optional, Generator
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import random
from .config import Config
from .registry import Registry
from .types import PacketData, SessionData, FlowData, ProtocolType
from ..common.logger import get_logger
from ..common.exceptions import TrafficLabError


class Engine:
    """Main engine for traffic generation and analysis.""" 
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.registry = Registry()
        self.logger = get_logger(__name__)
        self._sessions: List[SessionData] = []
        self._packets: List[PacketData] = []
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None
        
        if self.config.seed is not None:
            random.seed(self.config.seed)
    
    def generate(self) -> Generator[PacketData, None, None]:
        """Generate packets based on configuration."""
        self.logger.info("Starting packet generation")
        self._start_time = datetime.now()
        self._end_time = self._start_time + timedelta(seconds=self.config.duration)
        
        # Load profile
        from ..profiles import load_profile
        profile = load_profile(self.config.profile)
        
        # Generate sessions
        session_generator = self._create_session_generator(profile)
        
        packet_count = 0
        while datetime.now() < self._end_time:
            for packet in session_generator.generate():
                yield packet
                packet_count += 1
                
                if packet_count % 1000 == 0:
                    self.logger.info(f"Generated {packet_count} packets")
        
        self.logger.info(f"Packet generation complete. Total: {packet_count}")
    
    async def generate_async(self) -> List[PacketData]:
        """Generate packets asynchronously."""
        packets = []
        for packet in self.generate():
            packets.append(packet)
            if len(packets) % 100 == 0:
                await asyncio.sleep(0)  # Yield control
        return packets
    
    def analyze(self, packets: List[PacketData]) -> dict:
        """Analyze packet data."""
        self.logger.info("Starting packet analysis")
        
        analysis_results = {
            "total_packets": len(packets),
            "total_bytes": sum(p.length for p in packets),
            "protocol_distribution": {},
            "top_talkers": [],
            "packet_size_histogram": [],
            "flows": [],
        }
        
        # Protocol distribution
        for packet in packets:
            protocol = packet.protocol.value
            analysis_results["protocol_distribution"][protocol] = \
                analysis_results["protocol_distribution"].get(protocol, 0) + 1
        
        # Flow analysis
        flows = self._extract_flows(packets)
        analysis_results["flows"] = [
            {
                "id": flow.flow_id,
                "protocol": flow.protocol.value,
                "packets": flow.packet_count,
                "bytes": flow.byte_count,
                "duration": flow.duration,
            }
            for flow in flows[:10]  # Top 10 flows
        ]
        
        # Top talkers
        talkers = {}
        for packet in packets:
            src = packet.source.ipv4 or packet.source.mac or "unknown"
            talkers[src] = talkers.get(src, 0) + packet.length
        
        sorted_talkers = sorted(talkers.items(), key=lambda x: x[1], reverse=True)
        analysis_results["top_talkers"] = [
            {"address": addr, "bytes": bytes} 
            for addr, bytes in sorted_talkers[:10]
        ]
        
        # Packet size histogram
        size_bins = [0, 64, 128, 256, 512, 1024, 1500, 9000]
        hist = {}
        for packet in packets:
            size = packet.length
            for bin_size in size_bins:
                if size <= bin_size:
                    hist[bin_size] = hist.get(bin_size, 0) + 1
                    break
            else:
                hist["9000+"] = hist.get("9000+", 0) + 1
        
        analysis_results["packet_size_histogram"] = [
            {"size": str(k), "count": v} for k, v in hist.items()
        ]
        
        self.logger.info("Analysis complete")
        return analysis_results
    
    def _create_session_generator(self, profile):
        """Create session generator based on profile."""
        from ..generators.session_generator import SessionGenerator
        from ..generators.timing import PoissonTiming
        
        timing = PoissonTiming(
            mean=self.config.timing.mean_interval,
            burst_factor=self.config.timing.burst_factor
        )
        
        return SessionGenerator(
            profile=profile,
            config=self.config,
            timing=timing,
        )
    
    def _extract_flows(self, packets: List[PacketData]) -> List[FlowData]:
        """Extract flows from packets."""
        flows_dict = {}
        
        for packet in packets:
            # Create flow key
            key = f"{packet.source.ipv4}:{packet.source.port}->{packet.destination.ipv4}:{packet.destination.port}:{packet.protocol.value}"
            
            if key not in flows_dict:
                flows_dict[key] = FlowData(
                    flow_id=key,
                    source=packet.source,
                    destination=packet.destination,
                    protocol=packet.protocol,
                    start_time=packet.timestamp,
                )
            
            flows_dict[key].add_packet(packet)
        
        return list(flows_dict.values())
    
    def export(self, packets: List[PacketData], format: str, path: Path) -> None:
        """Export packets to file."""
        self.logger.info(f"Exporting {len(packets)} packets to {format} format")
        
        exporter_class = self.registry.get_exporter(format)
        if not exporter_class:
            raise TrafficLabError(f"Unsupported export format: {format}")
        
        exporter = exporter_class()
        exporter.export(packets, path)
        self.logger.info(f"Export complete: {path}")
    
    def import_pcap(self, path: Path) -> List[PacketData]:
        """Import packets from PCAP file."""
        self.logger.info(f"Importing PCAP: {path}")
        
        from ..importers.pcap_importer import PcapImporter
        
        importer = PcapImporter()
        packets = importer.import_file(path)
        self.logger.info(f"Imported {len(packets)} packets")
        return packets
    
    def get_statistics(self, packets: List[PacketData]) -> dict:
        """Get comprehensive statistics."""
        from ..statistics.stats import StatisticsEngine
        
        stats_engine = StatisticsEngine()
        return stats_engine.analyze(packets)
