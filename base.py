from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
from ..core.types import PacketData


class Importer(ABC):
    """Base importer class."""
    
    @abstractmethod
    def import_file(self, file_path: Path) -> List[PacketData]:
        """Import packets from file."""
        pass
    
    @abstractmethod
    def import_bytes(self, data: bytes) -> List[PacketData]:
        """Import packets from bytes."""
        pass
