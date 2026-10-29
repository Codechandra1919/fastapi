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

"""Entity-Klasse für den Mietvertrag."""

from typing import override
lazy from decimal import Decimal

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mieter.entity.base import Base
from mieter.entity.mieter import Mieter


class Mietvertrag(Base):
    """Entity-Klasse für den Mietvertrag."""

    __tablename__ = "mietvertrag"

    seiten_anz: Mapped[int]
    """Die Anzahl der Seiten des Mietvertrags."""

    kaution: Mapped[Decimal]
    """Die Kaution des Mietvertrags."""

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID gemäß der zugehörigen IDENTITY-Spalte."""

    mieter_id: Mapped[int | None] = mapped_column(ForeignKey("mieter.id"))
    """ID des zugehörigen Mieters als Fremdschlüssel in der DB-Tabelle."""

    mieter: Mapped[Mieter | None] = relationship(back_populates=Mieter.mietvertrag)
    """Das zugehörige transiente Mieter-Objekt."""

    # __repr__ fuer Entwickler/innen, __str__ fuer User
    @override
    def __repr__(self) -> str:
        """Ausgabe eines Mietvertrags als String ohne die Mieterdaten."""
        return (
            f"Mietvertrag(id={self.id}, seiten_anz={self.seiten_anz},"
            f" kaution={self.kaution})"
        )
