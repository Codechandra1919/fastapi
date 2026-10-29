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

"""Pydantic-Modelle für das Lesen von Mieterdaten."""

from typing import Annotated
lazy from datetime import date
lazy from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from mieter.repository import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    MieterSuchparameter,
    Pageable,
)
lazy from mieter.service import MieterDTO

__all__ = [
    "MieterFindModel",
    "MieterPageModel",
    "MieterResponseModel",
    "MietrechnungResponseModel",
    "MietvertragResponseModel",
]


class MieterFindModel(BaseModel):
    """Suchparameter und Pagination für die Mietersuche."""

    email: str | None = None
    nachname: str | None = None
    page: Annotated[int, Field(ge=DEFAULT_PAGE_NUMBER)] = DEFAULT_PAGE_NUMBER
    size: Annotated[int, Field(ge=0, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE

    # Keine weiteren Attribute erlaubt
    # unveraenderlich
    # https://pydantic.dev/docs/validation/latest/concepts/config
    # https://pydantic.dev/docs/validation/latest/api/pydantic/config
    model_config = ConfigDict(extra="forbid", frozen=True)

    def to_pageable(self) -> Pageable:
        """Erzeugt die Pagination-Daten aus den validierten Parametern."""
        return Pageable(number=self.page, size=self.size)

    def to_suchparameter(self) -> MieterSuchparameter:
        """Erzeugt Suchparameter für den Service."""
        return MieterSuchparameter(email=self.email, nachname=self.nachname)


class MietvertragResponseModel(BaseModel):
    """Mietvertrag als Teil eines Model-Objekts für Mieter als Response.

    Damit beim Konvertieren von `MieterDTO` in `MieterResponseModel` auch die
    Attribute von `MietvertragDTO` übernommen werden, ist
    `ConfigDict(from_attributes=True)` notwendig. Siehe
    https://pydantic.dev/docs/validation/latest/concepts/models/#nested-attributes
    """

    seiten_anz: int
    kaution: Decimal

    model_config = ConfigDict(from_attributes=True, strict=True, extra="forbid")


class MietrechnungResponseModel(BaseModel):
    """Mietrechnung als Teil eines Model-Objekts für Mieter als Response."""

    id: int
    betrag: Decimal
    waehrung: str

    model_config = ConfigDict(from_attributes=True, strict=True, extra="forbid")


class MieterResponseModel(BaseModel):
    """Pydantic-Modell für einen gefundenen Mieter.

    FastAPI konvertiert implizit die Felder in JSON, z.B.
    date als String "2000-01-31".
    """

    id: int
    vorname: str
    nachname: str
    email: str
    telefonnummer: str | None = None
    geburtsdatum: date | None = None
    mietvertrag: MietvertragResponseModel
    username: str

    model_config = ConfigDict(from_attributes=True, strict=True, extra="forbid")
    # https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict

    @classmethod
    def from_dto(cls, mieter: MieterDTO) -> MieterResponseModel:
        """Konvertiert ein MieterDTO in ein Pydantic-Modell für einen Response.

        Der Aufruf von `model_validate` erfordert die Übernahme der korrespondierenden
        Attributwerte aus dem DTO-Objekt. Dafür ist `ConfigDict(from_attributes=True)`
        notwendig.
        Siehe https://pydantic.dev/docs/validation/latest/concepts/models/#arbitrary-class-instances
        Der Aufwand für (unnötige) Validierung ist dabei minimal:
        https://pydantic.dev/docs/validation/latest/concepts/models/#creating-models-without-validation
        """
        return cls.model_validate(mieter)


class PageMetaModel(BaseModel):
    """Metadaten für eine Page mit Mieterdaten."""

    size: int
    number: int
    total_elements: int
    total_pages: int


class MieterPageModel(BaseModel):
    """Pydantic-Modell für einen Response bei einer Suche mit Pagination."""

    content: tuple[MieterResponseModel, ...]
    page: PageMetaModel
