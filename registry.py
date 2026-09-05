from typing import Dict, Type, Any, Callable, Optional
from functools import wraps
import inspect

class Registry:
    """Component registry with plugin support."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self) -> None:
        """Initialize registry."""
        self._protocols: Dict[str, Type] = {}
        self._builders: Dict[str, Type] = {}
        self._exporters: Dict[str, Type] = {}
        self._analyzers: Dict[str, Type] = {}
        self._generators: Dict[str, Type] = {}
        self._plugins: Dict[str, Any] = {}
    
    def register_protocol(self, name: str) -> Callable:
        """Decorator to register protocol."""
        def decorator(cls: Type) -> Type:
            self._protocols[name] = cls
            return cls
        return decorator
    
    def register_builder(self, name: str) -> Callable:
        """Decorator to register builder."""
        def decorator(cls: Type) -> Type:
            self._builders[name] = cls
            return cls
        return decorator
    
    def register_exporter(self, name: str) -> Callable:
        """Decorator to register exporter."""
        def decorator(cls: Type) -> Type:
            self._exporters[name] = cls
            return cls
        return decorator
    
    def register_analyzer(self, name: str) -> Callable:
        """Decorator to register analyzer."""
        def decorator(cls: Type) -> Type:
            self._analyzers[name] = cls
            return cls
        return decorator
    
    def register_generator(self, name: str) -> Callable:
        """Decorator to register generator."""
        def decorator(cls: Type) -> Type:
            self._generators[name] = cls
            return cls
        return decorator
    
    def register_plugin(self, name: str, plugin: Any) -> None:
        """Register a plugin."""
        self._plugins[name] = plugin
    
    def get_protocol(self, name: str) -> Optional[Type]:
        """Get protocol class by name."""
        return self._protocols.get(name)
    
    def get_builder(self, name: str) -> Optional[Type]:
        """Get builder class by name."""
        return self._builders.get(name)
    
    def get_exporter(self, name: str) -> Optional[Type]:
        """Get exporter class by name."""
        return self._exporters.get(name)
    
    def get_analyzer(self, name: str) -> Optional[Type]:
        """Get analyzer class by name."""
        return self._analyzers.get(name)
    
    def get_generator(self, name: str) -> Optional[Type]:
        """Get generator class by name."""
        return self._generators.get(name)
    
    def list_protocols(self) -> list:
        """List all registered protocols."""
        return list(self._protocols.keys())
    
    def list_builders(self) -> list:
        """List all registered builders."""
        return list(self._builders.keys())
    
    def list_exporters(self) -> list:
        """List all registered exporters."""
        return list(self._exporters.keys())
    
    def list_plugins(self) -> list:
        """List all registered plugins."""
        return list(self._plugins.keys())
