from abc import ABC, abstractmethod
from typing import Iterator, List, Any, Optional
from ..core.types import PacketData, SessionData
from ..core.config import Config
from ..profiles.base import Profile


class Generator(ABC):
    """Base generator class."""
    
    def __init__(self, config: Config, profile: Optional[Profile] = None):
        self.config = config
        self.profile = profile
        self._initialized = False
    
    @abstractmethod
    def generate(self) -> Iterator[PacketData]:
        """Generate packets."""
        pass
    
    @abstractmethod
    async def generate_async(self) -> List[PacketData]:
        """Generate packets asynchronously."""
        pass
    
    def initialize(self) -> None:
        """Initialize generator."""
        if not self._initialized:
            self._do_initialize()
            self._initialized = True
    
    def _do_initialize(self) -> None:
        """Perform initialization."""
        pass
