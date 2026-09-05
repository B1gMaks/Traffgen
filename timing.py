import random
import math
from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
from dataclasses import dataclass, field


class Timing(ABC):
    """Abstract timing model."""
    
    @abstractmethod
    def next_interval(self) -> float:
        """Get next time interval."""
        pass
    
    @abstractmethod
    def next_burst(self) -> Tuple[float, int]:
        """Get next burst (interval, size)."""
        pass


class FixedTiming(Timing):
    """Fixed interval timing."""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
    
    def next_interval(self) -> float:
        return self.interval
    
    def next_burst(self) -> Tuple[float, int]:
        return self.interval, 1


class UniformTiming(Timing):
    """Uniform distribution timing."""
    
    def __init__(self, min_interval: float = 0.5, max_interval: float = 2.0):
        self.min_interval = min_interval
        self.max_interval = max_interval
    
    def next_interval(self) -> float:
        return random.uniform(self.min_interval, self.max_interval)
    
    def next_burst(self) -> Tuple[float, int]:
        interval = self.next_interval()
        size = random.randint(1, 5)
        return interval, size


class NormalTiming(Timing):
    """Normal distribution timing."""
    
    def __init__(self, mean: float = 1.0, std: float = 0.3):
        self.mean = mean
        self.std = std
    
    def next_interval(self) -> float:
        interval = random.gauss(self.mean, self.std)
        return max(0.01, interval)
    
    def next_burst(self) -> Tuple[float, int]:
        interval = self.next_interval()
        size = max(1, int(random.gauss(3, 1)))
        return interval, size


class PoissonTiming(Timing):
    """Poisson arrival process timing."""
    
    def __init__(self, mean: float = 1.0, burst_factor: float = 0.0):
        self.mean = mean
        self.burst_factor = burst_factor  # 0 = no bursts, 1 = high burst
    
    def next_interval(self) -> float:
        # Poisson process: exponential distribution
        return random.expovariate(1.0 / self.mean) if self.mean > 0 else 1.0
    
    def next_burst(self) -> Tuple[float, int]:
        interval = self.next_interval()
        
        # Add burstiness
        if random.random() < self.burst_factor:
            # Burst: multiple packets close together
            burst_size = random.randint(2, 10)
            interval = interval / burst_size
        else:
            burst_size = 1
        
        return interval, burst_size


class BurstTiming(Timing):
    """Burst timing model with idle periods."""
    
    def __init__(
        self,
        burst_interval: float = 0.1,
        burst_size: int = 10,
        idle_interval: float = 5.0,
        idle_probability: float = 0.3,
    ):
        self.burst_interval = burst_interval
        self.burst_size = burst_size
        self.idle_interval = idle_interval
        self.idle_probability = idle_probability
        self._in_burst = False
        self._burst_count = 0
    
    def next_interval(self) -> float:
        if self._in_burst:
            self._burst_count += 1
            if self._burst_count >= self.burst_size:
                self._in_burst = False
                self._burst_count = 0
                return self.idle_interval
            return self.burst_interval
        else:
            if random.random() < self.idle_probability:
                return self.idle_interval
            else:
                self._in_burst = True
                self._burst_count = 0
                return self.burst_interval
    
    def next_burst(self) -> Tuple[float, int]:
        interval = self.next_interval()
        if self._in_burst:
            size = self.burst_size - self._burst_count
        else:
            size = 1
        return interval, size
