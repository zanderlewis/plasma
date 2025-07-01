"""License templates for project initialization."""

from .apache import APACHE_LICENSE
from .gpl import GPL_LICENSE
from .mit import MIT_LICENSE
from .unlicense import UNLICENSE

__all__ = ["APACHE_LICENSE", "GPL_LICENSE", "MIT_LICENSE", "UNLICENSE"]

LICENSES = [
    {"name": "MIT License", "identifier": "mit", "content": MIT_LICENSE},
    {"name": "Apache License 2.0", "identifier": "apache", "content": APACHE_LICENSE},
    {
        "name": "GNU General Public License v3.0",
        "identifier": "gpl",
        "content": GPL_LICENSE,
    },
    {"name": "Unlicense", "identifier": "unlicense", "content": UNLICENSE},
]
