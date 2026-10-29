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

"""Pydantic-Model für die Mieterdaten."""

from typing import Annotated, Final, override

from loguru import logger
from pydantic import ConfigDict, StringConstraints

from mieter.router.mieter_update_model import MieterUpdateModel
lazy from mieter.entity import Mieter
lazy from mieter.router.mietrechnung_model import MietrechnungModel
lazy from mieter.router.mietvertrag_model import MietvertragModel

__all__ = ["MieterModel"]


# https://towardsdatascience.com/pydantic-or-dataclasses-why-not-both-convert-between-them-ba382f0f9a9c
class MieterModel(MieterUpdateModel):
    """Pydantic-Model für die Mieterdaten beim Anlegen."""

    mietvertrag: MietvertragModel
    """Der zugehörige Mietvertrag."""

    mietrechnungen: list[MietrechnungModel]
    """Die Liste der Mietrechnungen."""

    username: Annotated[str, StringConstraints(max_length=20)]
    """Der Benutzername für Login."""

    # https://docs.pydantic.dev/latest/concepts/strict_mode/#as-a-configuration-value
    # https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data
    # https://pydantic.dev/docs/validation/latest/concepts/models/#faux-immutability
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    @override
    def to_mieter(self) -> Mieter:
        """Konvertierung in ein Mieter-Objekt für SQLAlchemy.

        :return: Mieter-Objekt für SQLAlchemy
        :rtype: Mieter
        """
        logger.debug("self={}", self)
        mieter: Final = super().to_mieter()
        mieter.mietvertrag = self.mietvertrag.to_mietvertrag()
        mieter.mietrechnungen = [
            mietrechnung_model.to_mietrechnung()
            for mietrechnung_model in self.mietrechnungen
        ]
        mieter.username = self.username
        logger.debug("mieter={}", mieter)
        return mieter
