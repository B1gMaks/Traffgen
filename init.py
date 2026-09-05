from .base import Profile, Host, Service, TrafficPattern
from .enterprise import EnterpriseProfile
from .office import OfficeProfile
from .home import HomeProfile
from .university import UniversityProfile
from .iot import IoTProfile
from .cloud import CloudProfile
from .datacenter import DataCenterProfile
from .isp import ISPProfile
from .industrial import IndustrialProfile
from .telecom import TelecomProfile


def load_profile(name: str) -> Profile:
    """Load a profile by name."""
    profiles = {
        "enterprise": EnterpriseProfile,
        "office": OfficeProfile,
        "home": HomeProfile,
        "university": UniversityProfile,
        "iot": IoTProfile,
        "cloud": CloudProfile,
        "datacenter": DataCenterProfile,
        "isp": ISPProfile,
        "industrial": IndustrialProfile,
        "telecom": TelecomProfile,
    }
    
    profile_class = profiles.get(name.lower())
    if not profile_class:
        raise ValueError(f"Unknown profile: {name}")
    
    return profile_class()


__all__ = [
    "Profile",
    "Host",
    "Service",
    "TrafficPattern",
    "EnterpriseProfile",
    "OfficeProfile",
    "HomeProfile",
    "UniversityProfile",
    "IoTProfile",
    "CloudProfile",
    "DataCenterProfile",
    "ISPProfile",
    "IndustrialProfile",
    "TelecomProfile",
    "load_profile",
]
