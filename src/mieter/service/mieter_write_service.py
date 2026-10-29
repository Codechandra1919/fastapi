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

"""Geschäftslogik zum Schreiben von Mieterdaten."""

from typing import Final

from loguru import logger

from mieter.repository import MieterRepository, Session
from mieter.security import User, UserService
from mieter.service.exceptions import (
    EmailExistsError,
    EmptyUsernameError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)
from mieter.service.mieter_dto import MieterDTO
lazy from mieter.entity import Mieter

__all__ = ["MieterWriteService"]


class MieterWriteService:
    """Service-Klasse mit Geschäftslogik für Mieter."""

    def __init__(self, repo: MieterRepository, user_service: UserService) -> None:
        """Konstruktor mit abhängigem MieterRepository und UserService."""
        self.repo: MieterRepository = repo
        self.user_service: UserService = user_service

    def create(self, mieter: Mieter) -> MieterDTO:
        """Einen neuen Mieter anlegen.

        :param mieter: Der neue Mieter ohne ID
        :return: Der neu angelegte Mieter mit generierter ID
        :rtype: MieterDTO
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        :raises EmptyUsernameError: Falls der Benutzername leer ist
        :raises UsernameExistsError: Falls der Benutzername bereits existiert
        """
        logger.debug(
            "mieter={}, mietvertrag={}, mietrechnungen={}",
            mieter,
            mieter.mietvertrag,
            mieter.mietrechnungen,
        )

        username: Final = mieter.username
        if username is None or not username.strip():
            raise EmptyUsernameError
        if self.user_service.username_exists(username):
            raise UsernameExistsError(username=username)

        email: Final = mieter.email
        if self.user_service.email_exists(email):
            raise EmailExistsError(email=email)

        user: Final = User(
            username=username,
            email=mieter.email,
            nachname=mieter.nachname,
            vorname=mieter.vorname,
            password="p",  # ruff: ignore[hardcoded-password-func-arg] # NOSONAR
            roles=[],
        )
        user_id = self.user_service.create_user(user)
        logger.debug("user_id={}", user_id)

        # durch "with" erhaelt man einen "Context Manager", der die Ressource/Session
        # am Endes des Blocks schliesst
        with Session() as session:
            if self.repo.exists_email(email=email, session=session):
                raise EmailExistsError(email=email)

            mieter_db: Final = self.repo.create(mieter=mieter, session=session)
            mieter_dto: Final = MieterDTO.from_mieter(mieter_db)
            session.commit()

        # TODO User aus Keycloak loeschen, falls die DB-Transaktion fehlschlaegt

        logger.debug("mieter_dto={}", mieter_dto)
        return mieter_dto

    def update(self, mieter: Mieter, mieter_id: int, version: int) -> MieterDTO:
        """Daten eines Mieters ändern.

        :param mieter: Die neuen Daten
        :param mieter_id: ID des zu aktualisierenden Mieters
        :param version: Version für optimistische Synchronisation
        :return: Der aktualisierte Mieter
        :rtype: MieterDTO
        :raises NotFoundError: Falls der zu aktualisierende Mieter nicht existiert
        :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug("mieter_id={}, version={}, {}", mieter_id, version, mieter)

        with Session() as session:
            if (
                mieter_db := self.repo.find_by_id(
                    mieter_id=mieter_id,
                    session=session,
                )
            ) is None:
                raise NotFoundError(mieter_id)
            if mieter_db.version > version:
                raise VersionOutdatedError(version)

            email: Final = mieter.email
            if email != mieter_db.email and self.repo.exists_email_other_id(
                mieter_id=mieter_id,
                email=email,
                session=session,
            ):
                raise EmailExistsError(email)

            mieter_db.set(mieter)
            if (
                mieter_updated := self.repo.update(mieter=mieter_db, session=session)
            ) is None:
                raise NotFoundError(mieter_id)
            mieter_dto: Final = MieterDTO.from_mieter(mieter_updated)
            logger.debug("{}", mieter_dto)

            session.commit()
            # CAVEAT: Die erhoehte Versionsnummer ist erst nach COMMIT sichtbar
            mieter_dto.version += 1
            return mieter_dto

    def delete_by_id(self, mieter_id: int) -> None:
        """Einen Mieter anhand seiner ID löschen.

        :param mieter_id: ID des zu löschenden Mieters
        """
        logger.debug("mieter_id={}", mieter_id)
        with Session() as session:
            self.repo.delete_by_id(mieter_id=mieter_id, session=session)
            session.commit()
