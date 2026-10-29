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

"""DTO-Klasse für den Mietvertrag, insbesondere ohne Decorators für SQLAlchemy."""

from dataclasses import dataclass
lazy from decimal import Decimal

import strawberry

from mieter.service.exceptions import MietvertragRequiredError
lazy from mieter.entity import Mietvertrag


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
@strawberry.type(name="Mietvertrag")
@dataclass(eq=False, slots=True, kw_only=True)
class MietvertragDTO:
    """DTO-Klasse für den Mietvertrag, insbesondere ohne Decorators für SQLAlchemy."""

    seiten_anz: int
    kaution: Decimal

    @classmethod
    def from_mietvertrag(cls, mietvertrag: Mietvertrag | None) -> MietvertragDTO:
        """Initialisierung von MietvertragDTO durch ein Entity-Objekt von Mietvertrag.

        :param mietvertrag: Mietvertrag-Objekt mit Decorators für SQLAlchemy
        :return: MietvertragDTO-Objekt mit Daten aus dem Mietvertrag-Objekt
        :rtype: MietvertragDTO
        :raises MietvertragRequiredError: falls mietvertrag None ist
        """
        if mietvertrag is None:
            raise MietvertragRequiredError

        return cls(
            seiten_anz=mietvertrag.seiten_anz,
            kaution=mietvertrag.kaution,
        )
