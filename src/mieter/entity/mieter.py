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

"""Entity-Klasse für Mieterdaten."""

from typing import Self, override
lazy from datetime import date, datetime

from sqlalchemy import Identity, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mieter.entity.base import Base
lazy from mieter.entity.mietrechnung import Mietrechnung
lazy from mieter.entity.mietvertrag import Mietvertrag


class Mieter(Base):
    """Entity-Klasse für Mieterdaten."""

    __tablename__ = "mieter"

    vorname: Mapped[str]
    """Der Vorname."""

    nachname: Mapped[str]
    """Der Nachname."""

    email: Mapped[str] = mapped_column(unique=True)
    """Die eindeutige Emailadresse."""

    telefonnummer: Mapped[str | None]
    """Die optionale Telefonnummer."""

    geburtsdatum: Mapped[date | None]
    """Das optionale Geburtsdatum."""

    username: Mapped[str | None]
    """Der Benutzername für Login."""

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    """Die generierte ID gemäß der zugehörigen IDENTITY-Spalte."""

    mietvertrag: Mapped[Mietvertrag | None] = relationship(
        back_populates=lambda: Mietvertrag.mieter,
        innerjoin=True,
        cascade="save-update, delete",
    )
    """Die in einer 1:1-Beziehung referenzierten Mietvertrag."""

    mietrechnungen: Mapped[list[Mietrechnung]] = relationship(
        back_populates=lambda: Mietrechnung.mieter,
        cascade="save-update, delete",
    )
    """Die in einer 1:N-Beziehung referenzierten Mietrechnungen."""

    erzeugt: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
    )
    """Der Zeitstempel für das initiale INSERT in die DB-Tabelle."""

    aktualisiert: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(),
        onupdate=func.now(),
    )
    """Der Zeitstempel vom letzten UPDATE in der DB-Tabelle."""

    version: Mapped[int] = mapped_column(nullable=False, default=0)
    """Die Versionsnummer für optimistische Synchronisation."""

    __mapper_args__ = {"version_id_col": version}  # ruff: ignore[mutable-class-default]

    def set(self, mieter: Self) -> None:
        """Primitive Attributwerte überschreiben, z.B. vor DB-Update.

        :param mieter: Mieter-Objekt mit den aktuellen Daten
        """
        self.vorname = mieter.vorname
        self.nachname = mieter.nachname
        self.email = mieter.email
        self.telefonnummer = mieter.telefonnummer
        self.geburtsdatum = mieter.geburtsdatum

    @override
    def __eq__(self, other: object) -> bool:
        """Vergleich auf Gleichheit, ohne Joins zu verursachen."""
        if self is other:
            return True
        if not isinstance(other, type(self)):
            return False
        return self.id is not None and self.id == other.id

    def __hash__(self) -> int:
        """Hash-Funktion anhand der ID, ohne Joins zu verursachen."""
        return hash(self.id) if self.id is not None else hash(type(self))

    # __repr__ fuer Entwickler/innen, __str__ fuer User
    @override
    def __repr__(self) -> str:
        """Ausgabe eines Mieters als String, ohne Joins zu verursachen."""
        return (
            f"Mieter(id={self.id}, version={self.version}, "
            f"vorname='{self.vorname}', nachname='{self.nachname}', "
            f"email='{self.email}', telefonnummer='{self.telefonnummer}', "
            f"geburtsdatum={self.geburtsdatum}, usernmame='{self.username}', "
            f"erzeugt={self.erzeugt}, aktualisiert={self.aktualisiert})"
        )
