"""Swiss Knife - A comprehensive collection of Python automation tools.

Automating the mundane, one tool at a time.
"""

__version__ = "0.1.0"
__author__ = "Ayoub Abidi"
__email__ = "ayoub3bidi@gmail.com"

from .core import SafetyError, ValidationError

__all__ = ["SafetyError", "ValidationError", "__version__"]
