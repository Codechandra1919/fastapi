"""Modul für den DB-Zugriff."""

from mieter.repository.mieter_repository import MieterRepository
from mieter.repository.mieter_suchparameter import MieterSuchparameter
from mieter.repository.pageable import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    Pageable,
)
from mieter.repository.session_factory import Session, engine
from mieter.repository.slice import Slice

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "DEFAULT_PAGE_NUMBER",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "MieterRepository",
    "MieterSuchparameter",
    "Pageable",
    "Session",
    "Slice",
    "engine",
]
