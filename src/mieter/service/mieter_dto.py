# Copyright (C) 2026 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""DTO-Klasse für Mieterdaten, insbesondere ohne Decorators für SQLAlchemy."""

from dataclasses import dataclass
lazy from datetime import date

import strawberry

from mieter.service.mietvertrag_dto import MietvertragDTO
lazy from mieter.entity import Mieter

__all__ = ["MieterDTO"]


# Mit der Funktion asdict() kann ein Objekt einfach in ein dict konvertiert werden
# init=True (default): __init__ fuer die "member variables" wird generiert
# eq=True (default): __eq__ wird generiert
# unsafe_hash=False (default): __hash__ passend zu __eq__ wird generiert
# repr=True (default): __repr__ wird generiert
# frozen=False (default): mutable
# kw_only=False (default): Initialisierungs-Fkt auch ohne "Keyword Arguments" aufrufen
# slots=False (default): __dict__ zur Speicherung statt slots
# slots: schnellerer Zugriff, kompakte Speicherung
# https://stackoverflow.com/questions/472000/usage-of-slots
# Strawberry konvertiert automatisch zwischen snake_case (Python) und camelCase (Schema)
@strawberry.type(name="Mieter")
@dataclass(eq=False, slots=True, kw_only=True)
class MieterDTO:
    """DTO-Klasse für ausgelesene oder gespeicherte Mieterdaten: ohne Decorators."""

    id: int
    version: int
    vorname: str
    nachname: str
    email: str
    telefonnummer: str | None
    # https://docs.python.org/3/library/datetime.html
    geburtsdatum: date | None
    mietvertrag: MietvertragDTO
    username: str

    # https://github.com/python/cpython/issues/94345
    @classmethod
    def from_mieter(cls, mieter: Mieter) -> MieterDTO:
        """Initialisierung von MieterDTO durch ein Entity-Objekt von Mieter.

        :param mieter: Mieter-Objekt mit Decorators zu SQLAlchemy
        :return: MieterDTO-Objekt mit Daten aus dem Mieter-Objekt
        :rtype: MieterDTO
        """
        return cls(
            id=mieter.id if mieter.id is not None else -1,
            version=mieter.version,
            vorname=mieter.vorname,
            nachname=mieter.nachname,
            email=mieter.email,
            telefonnummer=mieter.telefonnummer,
            geburtsdatum=mieter.geburtsdatum,
            mietvertrag=MietvertragDTO.from_mietvertrag(mieter.mietvertrag),
            username=mieter.username if mieter.username is not None else "N/A",
        )
