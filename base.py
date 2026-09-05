from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path
from enum import Enum
from ..core.types import PacketData


class ExportFormat(str, Enum):
    """Supported export formats."""
    
    PCAP = "pcap"
    PCAPNG = "pcapng"
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"


class Exporter(ABC):
    """Base exporter class."""
    
    def __init__(self):
        self._packets: List[PacketData] = []
        self._metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def export(self, packets: List[PacketData], output_path: Path, **kwargs) -> None:
        """Export packets to file."""
        pass
    
    @abstractmethod
    def export_string(self, packets: List[PacketData], **kwargs) -> str:
        """Export packets as string."""
        pass
    
    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """Set metadata for export."""
        self._metadata = metadata
    
    def _prepare_packets(self, packets: List[PacketData]) -> List[Dict[str, Any]]:
        """Prepare packets for export."""
        return [p.to_dict() for p in packets]
