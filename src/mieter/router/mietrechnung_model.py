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

"""Pydantic-Model für die Mietrechnungen."""

from typing import Annotated
lazy from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from mieter.entity import Mietrechnung

__all__ = ["MietrechnungModel"]


class MietrechnungModel(BaseModel):
    """Pydantic-Model für die mietrechnung_dict."""

    betrag: Decimal = Field(strict=False)
    """Der Betrag. Keine strikte Validierung: JSON -> float in Python."""
    waehrung: Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]
    """Die Währung als 3-stelliger ISO-Code."""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra={
            "example": {
                "betrag": "999.99",
                "waehrung": "EUR",
            },
        },
        # https://docs.pydantic.dev/latest/concepts/strict_mode/#as-a-configuration-value
        strict=True,
        # https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data
        extra="forbid",
        # https://pydantic.dev/docs/validation/latest/concepts/models/#faux-immutability
        frozen=True,
    )

    def to_mietrechnung(self) -> Mietrechnung:
        """Konvertierung in ein Mietrechnung-Objekt für SQLAlchemy.

        :return: Mietrechnung-Objekt für SQLAlchemy
        :rtype: Mietrechnung
        """
        return Mietrechnung(
            id=None,
            betrag=self.betrag,
            waehrung=self.waehrung,
            mieter_id=None,
            mieter=None,
        )
