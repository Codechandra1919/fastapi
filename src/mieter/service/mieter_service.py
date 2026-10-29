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

"""Geschäftslogik zum Lesen von Mieterdaten."""

from datetime import datetime
from typing import Final
from zoneinfo import ZoneInfo
lazy from collections.abc import Sequence

from loguru import logger
from openpyxl import Workbook

from mieter.config import excel_enabled
from mieter.repository import (
    MieterRepository,
    MieterSuchparameter,
    Pageable,
    Session,
    Slice,
)
from mieter.security import Role, User
from mieter.service.exceptions import ForbiddenError, NotFoundError
from mieter.service.mieter_dto import MieterDTO

__all__ = ["MieterService"]


class MieterService:
    """Service-Klasse mit Geschäftslogik für Mieter."""

    def __init__(self, repo: MieterRepository) -> None:
        """Konstruktor mit abhängigem MieterRepository."""
        self.repo: MieterRepository = repo

    def find_by_id(self, mieter_id: int, user: User) -> MieterDTO:
        """Suche mit der Mieter-ID.

        :param mieter_id: ID für die Suche
        :param user: User aus dem Token
        :return: Der gefundene Mieter
        :rtype: MieterDTO
        :raises NotFoundError: Falls kein Mieter gefunden
        :raises ForbiddenError: Falls die Mieterdaten nicht gelesen werden dürfen
        """
        logger.debug("mieter_id={}, user={}", mieter_id, user)

        # Session-Objekt ist die Schnittstelle zur DB, nutzt intern ein Transaktionsobj.
        # implizites "autobegin()" bei einem with-Block
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#opening-and-closing-a-session
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#using-a-sessionmaker
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#auto-begin
        # durch "with" erhaelt man einen "Context Manager", der die Ressource/Session
        # am Endes des Blocks schliesst
        with Session() as session:
            user_is_admin: Final = Role.ADMIN in user.roles

            if (
                mieter := self.repo.find_by_id(session=session, mieter_id=mieter_id)
            ) is None:
                if user_is_admin:
                    message: Final = f"Kein Mieter mit der ID {mieter_id}"
                    logger.debug("NotFoundError: {}", message)
                    # "Throw Exceptions Instead of Returning Errors"
                    raise NotFoundError(mieter_id=mieter_id)
                logger.debug("nicht admin")
                raise ForbiddenError

            if not user_is_admin and (
                Role.MIETER not in user.roles or user.username != mieter.username
            ):
                logger.debug(
                    "mieter_id={}, user.username={}, user.roles={}",
                    mieter_id,
                    user.username,
                    user.roles,
                )
                raise ForbiddenError

            mieter_dto: Final = MieterDTO.from_mieter(mieter)
            session.commit()

        logger.debug("{}", mieter_dto)
        return mieter_dto

    # ab Python 3.9 (2019) ist der Element-Type in eckigen Klammern und
    # der Name von eingebauten Collections ist kleingeschrieben.
    def find(
        self,
        suchparameter: MieterSuchparameter | None,
        pageable: Pageable,
    ) -> Slice[MieterDTO]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter oder None
        :param pageable: Pagination-Informationen
        :return: Liste der gefundenen Mieter
        :rtype: Slice[MieterDTO]
        :raises NotFoundError: Falls keine Mieter gefunden wurden
        """
        logger.debug("{}", suchparameter)
        with Session() as session:
            mieter_slice: Final = self.repo.find(
                suchparameter=suchparameter,
                pageable=pageable,
                session=session,
            )
            if len(mieter_slice.content) == 0:
                raise NotFoundError(suchparameter=suchparameter)

            # tuple mit einem "Generator"-Ausdruck
            # vgl. List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
            mieter_dto_liste: Final = tuple(
                MieterDTO.from_mieter(mieter) for mieter in mieter_slice.content
            )
            session.commit()

        if excel_enabled:
            self._create_excelsheet(mieter_dto_liste)
        mieter_dto_slice = Slice(
            content=mieter_dto_liste,
            total_elements=mieter_slice.total_elements,
        )
        logger.debug("{}", mieter_dto_slice)
        return mieter_dto_slice

    def find_nachnamen(self, teil: str) -> Sequence[str]:
        """Suche Nachnamen zu einem Teilstring.

        :param teil: Teilstring der gesuchten Nachnamen
        :return: Liste der gefundenen Nachnamen oder eine leere Liste
        :rtype: Sequence[str]
        :raises NotFoundError: Falls keine Nachnamen gefunden wurden
        """
        logger.debug("teil={}", teil)
        with Session() as session:
            nachnamen: Final = self.repo.find_nachnamen(teil=teil, session=session)
            session.commit()

        logger.debug("{}", nachnamen)
        if len(nachnamen) == 0:
            raise NotFoundError
        return nachnamen

    def _create_excelsheet(self, mieter_liste: tuple[MieterDTO, ...]) -> None:
        """Ein Excelsheet mit den gefundenen Mietern erstellen.

        :param mieter_liste: Mieterdaten für das Excelsheet
        """
        # https://automatetheboringstuff.com/2e/chapter13
        workbook: Final = Workbook()
        worksheet: Final = workbook.active
        if worksheet is None:
            return

        worksheet.append(["Vorname", "Nachname", "Emailadresse", "Telefonnummer"])
        for mieter in mieter_liste:
            telefonnummer = (
                mieter.telefonnummer if mieter.telefonnummer is not None else "N/A"
            )
            worksheet.append((
                mieter.vorname,
                mieter.nachname,
                mieter.email,
                telefonnummer,
            ))

        timestamp: Final = datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime(
            format="%Y-%m-%d_%H%M%S",
        )
        workbook.save(f"mieter-{timestamp}.xlsx")
