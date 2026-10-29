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

"""Repository fuer persistente Mieterdaten."""

from typing import Final
lazy from collections.abc import Sequence

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from mieter.entity import Mieter
from mieter.repository.slice import Slice
lazy from mieter.repository.mieter_suchparameter import MieterSuchparameter
lazy from mieter.repository.pageable import Pageable

__all__ = ["MieterRepository"]


class MieterRepository:
    """Repository-Klasse mit CRUD-Methoden für die Entity-Klasse Mieter."""

    def find_by_id(self, mieter_id: int | None, session: Session) -> Mieter | None:
        """Suche mit der Mieter-ID.

        :param mieter_id: ID des gesuchten Mieters
        :param session: Session für SQLAlchemy
        :return: Der gefundene Mieter oder None
        :rtype: Mieter | None
        """
        logger.debug("mieter_id={}", mieter_id)  # NOSONAR

        if mieter_id is None:
            return None

        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#relationship-loading-with-loader-options
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#sqlalchemy.orm.joinedload
        statement: Final = (
            select(Mieter)
            .options(
                joinedload(Mieter.mietvertrag),
            )
            .where(Mieter.id == mieter_id)
        )
        mieter: Final = session.scalar(statement)

        logger.debug("{}", mieter)
        return mieter

    def find(
        self,
        suchparameter: MieterSuchparameter | None,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Mieter]:
        """Suche mit Suchparameter.

        :param suchparameter: Suchparameter oder None
        :param pageable: Anzahl Datensätze und Seitennummer
        :param session: Session für SQLAlchemy
        :return: Slice der gefundenen Mieter
        :rtype: Slice[Mieter]
        """
        log_str: Final = "{}"
        logger.debug(log_str, suchparameter)
        if suchparameter is None or suchparameter.is_empty():
            return self._find_all(pageable=pageable, session=session)

        if suchparameter.email is not None:
            mieter = self._find_by_email(email=suchparameter.email, session=session)
            logger.debug(log_str, mieter)
            return (
                Slice(content=(mieter,), total_elements=1)
                if mieter is not None
                else Slice(content=(), total_elements=0)
            )

        if suchparameter.nachname is not None:
            mieter_liste = self._find_by_nachname(
                teil=suchparameter.nachname,
                pageable=pageable,
                session=session,
            )
            logger.debug(log_str, mieter_liste)
            return mieter_liste

        return Slice(content=(), total_elements=0)

    def _find_all(self, pageable: Pageable, session: Session) -> Slice[Mieter]:
        logger.debug("aufgerufen")
        offset = pageable.number * pageable.size
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        statement: Final = (
            (
                select(Mieter)
                .options(
                    joinedload(Mieter.mietvertrag),
                )
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (
                select(Mieter).options(
                    joinedload(Mieter.mietvertrag),
                )
            )
        )
        mieter_liste: Final = (session.scalars(statement)).unique().all()
        anzahl: Final = self._count_all_rows(session)
        mieter_slice: Final = Slice(content=tuple(mieter_liste), total_elements=anzahl)
        logger.debug("mieter_slice={}", mieter_slice)
        return mieter_slice

    def _count_all_rows(self, session: Session) -> int:
        statement: Final = select(func.count()).select_from(Mieter)
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0

    def _find_by_email(self, email: str, session: Session) -> Mieter | None:
        """Einen Mieter anhand der Emailadresse suchen.

        :param email: Emailadresse
        :param session: Session für SQLAlchemy
        :return: Gefundener Mieter, falls es einen Mieter gibt, sonst None
        :rtype: Mieter | None
        """
        logger.debug("email={}", email)  # NOSONAR
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        statement: Final = (
            select(Mieter)
            .options(
                joinedload(Mieter.mietvertrag),
            )
            .where(Mieter.email == email)
        )
        mieter: Final = session.scalar(statement)
        logger.debug("{}", mieter)
        return mieter

    def _find_by_nachname(
        self,
        teil: str,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Mieter]:
        logger.debug("teil={}", teil)
        offset = pageable.number * pageable.size
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#querying
        statement: Final = (
            (
                select(Mieter)
                .options(
                    joinedload(Mieter.mietvertrag),
                )
                .filter(Mieter.nachname.ilike(f"%{teil}%"))
                .limit(pageable.size)
                .offset(offset)
            )
            if pageable.size != 0
            else (
                select(Mieter)
                .options(
                    joinedload(Mieter.mietvertrag),
                )
                .filter(Mieter.nachname.ilike(f"%{teil}%"))
            )
        )
        mieter_liste: Final = session.scalars(statement).unique().all()
        anzahl: Final = self._count_rows_nachname(teil, session)
        mieter_slice: Final = Slice(content=tuple(mieter_liste), total_elements=anzahl)
        logger.debug("{}", mieter_slice)
        return mieter_slice

    def _count_rows_nachname(self, teil: str, session: Session) -> int:
        statement: Final = (
            select(func.count())
            .select_from(Mieter)
            .filter(Mieter.nachname.ilike(f"%{teil}%"))
        )
        count: Final = session.execute(statement).scalar()
        return count if count is not None else 0

    def exists_email(self, email: str, session: Session) -> bool:
        """Abfrage, ob es die Emailadresse bereits gibt.

        :param email: Emailadresse
        :param session: Session für SQLAlchemy
        :return: True, falls es die Emailadresse bereits gibt, False sonst
        :rtype: bool
        """
        logger.debug("email={}", email)

        statement: Final = select(func.count()).where(Mieter.email == email)
        anzahl: Final = session.scalar(statement)
        logger.debug("anzahl={}", anzahl)
        return anzahl is not None and anzahl > 0

    def exists_email_other_id(
        self,
        email: str,
        mieter_id: int,
        session: Session,
    ) -> bool:
        """Abfrage, ob es die Emailadresse bei einer anderen Mieter-ID bereits gibt.

        :param email: Emailadresse
        :param mieter_id: eigene Mieter-ID
        :param session: Session für SQLAlchemy
        :return: True, falls es die Emailadresse bereits gibt, False sonst
        :rtype: bool
        """
        logger.debug("email={}", email)

        statement: Final = select(Mieter.id).where(Mieter.email == email)
        id_db: Final = session.scalar(statement)
        logger.debug("id_db={}", id_db)
        return id_db is not None and id_db != mieter_id

    def create(self, mieter: Mieter, session: Session) -> Mieter:
        """Speichere einen neuen Mieter ab.

        :param mieter: Die Daten des neuen Mieters ohne ID
        :param session: Session für SQLAlchemy
        :return: Der neu angelegte Mieter mit generierter ID
        :rtype: Mieter
        """
        logger.debug(
            "mieter={}, mieter.mietvertrag={}, mieter.mietrechnungen={}",
            mieter,
            mieter.mietvertrag,
            mieter.mietrechnungen,
        )
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#adding-new-or-existing-items
        session.add(instance=mieter)
        # flush(), damit die ID aus der Sequence vor COMMIT fuer Logging verfuegbar ist
        # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#flushing
        session.flush(objects=[mieter])
        logger.debug("mieter_id={}", mieter.id)
        return mieter

    def update(self, mieter: Mieter, session: Session) -> Mieter | None:
        """Aktualisiere einen Mieter.

        :param mieter: Die neuen Mieterdaten
        :param session: Session für SQLAlchemy
        :return: Der aktualisierte Mieter oder None, falls kein Mieter mit der ID
                 existiert
        :rtype: Mieter | None
        """
        logger.debug("{}", mieter)

        if (mieter_db := self.find_by_id(mieter_id=mieter.id, session=session)) is None:
            return None

        logger.debug("{}", mieter_db)
        return mieter_db

    def delete_by_id(self, mieter_id: int, session: Session) -> None:
        """Lösche die Daten zu einem Mieter.

        :param mieter_id: Die ID des zu löschenden Mieters
        :param session: Session für SQLAlchemy
        """
        logger.debug("mieter_id={}", mieter_id)

        if (mieter := self.find_by_id(mieter_id=mieter_id, session=session)) is None:
            return
        session.delete(mieter)
        logger.debug("ok")

    def find_nachnamen(self, teil: str, session: Session) -> Sequence[str]:
        """Suche Nachnamen zu einem Teilstring.

        :param teil: Teilstring zu den gesuchten Nachnamen
        :param session: Session für SQLAlchemy
        :return: Liste der gefundenen Nachnamen oder eine leere Liste
        :rtype: Sequence[str]
        """
        logger.debug("teil={}", teil)

        statement: Final = (
            select(Mieter.nachname)
            .filter(Mieter.nachname.ilike(f"%{teil}%"))
            .distinct()
        )
        nachnamen: Final = (session.scalars(statement)).all()

        logger.debug("nachnamen={}", nachnamen)
        return nachnamen
