"""Database models package."""
from .violation import Violation, db
from .location import Location
from .violation_fine import ViolationFine
from .cached_query import CachedQuery
