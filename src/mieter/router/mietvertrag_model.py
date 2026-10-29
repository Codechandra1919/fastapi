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

"""Pydantic-Model für den Mietvertrag."""

from typing import Annotated
lazy from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from mieter.entity import Mietvertrag

__all__ = ["MietvertragModel"]


class MietvertragModel(BaseModel):
    """Pydantic-Model für den Mietvertrag."""

    seiten_anz: Annotated[int, Field(gt=0)]
    """Anzahl der Seiten des Mietvertrags (muss größer als 0 sein)."""

    kaution: Annotated[Decimal, Field(ge=Decimal(0), decimal_places=2, strict=False)]
    """Kaution des Mietvertrags (muss positiv oder 0 sein)."""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra={
            "example": {
                "seiten_anz": 12,
                "kaution": 1500.00,
            },
        },
        # https://docs.pydantic.dev/latest/concepts/strict_mode/#as-a-configuration-value
        strict=True,
        # https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data
        extra="forbid",
        # https://pydantic.dev/docs/validation/latest/concepts/models/#faux-immutability
        frozen=True,
    )

    def to_mietvertrag(self) -> Mietvertrag:
        """Konvertierung in ein Mietvertrag-Objekt für SQLAlchemy.

        :return: Mietvertrag-Objekt für SQLAlchemy
        :rtype: Mietvertrag
        """
        return Mietvertrag(
            id=None,
            seiten_anz=self.seiten_anz,
            kaution=self.kaution,
            mieter_id=None,
            mieter=None,
        )
