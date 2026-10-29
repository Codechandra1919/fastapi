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

"""Pydantic-Model zum Aktualisieren von Mieterdaten."""

from typing import Annotated
lazy from datetime import date

from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from mieter.entity import Mieter

__all__ = ["MieterUpdateModel"]


class MieterUpdateModel(BaseModel):
    """Pydantic-Model zum Aktualisieren von Mieterdaten."""

    # https://docs.pydantic.dev/latest/usage/types
    vorname: Annotated[
        str,
        StringConstraints(
            pattern=r"^[A-ZÄÖÜ][a-zäöüß]+(-[A-ZÄÖÜ][a-zäöüß])?$",
            max_length=64,
        ),
    ]
    """Der Vorname."""

    nachname: Annotated[
        str,
        StringConstraints(
            pattern=r"^[A-ZÄÖÜ][a-zäöüß]+(-[A-ZÄÖÜ][a-zäöüß])?$",
            max_length=64,
        ),
    ]
    """Der Nachname."""

    email: EmailStr
    """Die eindeutige Emailadresse."""

    telefonnummer: Annotated[
        str | None,
        StringConstraints(pattern=r"^\+?[0-9\s\-/]{6,30}$"),
    ] = None
    """Die optionale Telefonnummer."""

    geburtsdatum: date | None = Field(default=None, strict=False)
    """Das optionale Geburtsdatum. Keine strikte Validierung: String in JSON."""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra={
            "example": {
                "vorname": "Max",
                "nachname": "Mustermann",
                "email": "max.mustermann@acme.com",
                "telefonnummer": "+49 123 456789",
                "geburtsdatum": "1995-05-15",
                "username": "maxmustermann",
            },
        },
        # https://docs.pydantic.dev/latest/concepts/strict_mode/#as-a-configuration-value
        strict=True,
        # https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data
        extra="forbid",
        # https://pydantic.dev/docs/validation/latest/concepts/models/#faux-immutability
        frozen=True,
    )

    def to_mieter(self) -> Mieter:
        """Konvertierung in ein Mieter-Objekt für SQLAlchemy.

        :return: Mieter-Objekt für SQLAlchemy ohne Mietvertrag und Mietrechnungen.
        :rtype: Mieter
        """
        logger.debug("self={}", self)
        mieter = Mieter(
            id=None,
            vorname=self.vorname,
            nachname=self.nachname,
            email=self.email,
            telefonnummer=self.telefonnummer,
            geburtsdatum=self.geburtsdatum,
            mietvertrag=None,
            mietrechnungen=[],
            username=None,
            erzeugt=None,
            aktualisiert=None,
        )
        logger.debug("mieter={}", mieter)
        return mieter
