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

"""Schema für GraphQL durch Strawberry.

Alternative: https://github.com/graphql-python/graphene.
"""

from dataclasses import asdict
from typing import Final
lazy from collections.abc import Sequence

import strawberry
from fastapi import Request
from loguru import logger
from strawberry.extensions import PydanticErrorExtension
from strawberry.fastapi import GraphQLRouter
lazy from strawberry.types import Info

from mieter.config.graphql import graphql_ide
from mieter.graphql_api.graphql_types import (
    CreatePayload,
    LoginResult,
    MieterInput,
    Suchparameter,
)
from mieter.repository import MieterRepository, MieterSuchparameter, Pageable
from mieter.router.mieter_model import MieterModel
from mieter.security import Role, TokenService, UserService
from mieter.service import (
    MieterDTO,
    MieterService,
    MieterWriteService,
    NotFoundError,
)

__all__ = ["graphql_router"]


# Strawberry ist eine "code-first library":
# - keine Schema-Datei in SDL (schema definition language) notwendig
# - das Schema wird aus Klassen generiert, die mit z.B. @type oder @input dekoriert sind

# type Mieter {
#     nachname: String!
# }
# input Suchparameter {...}
# type Query {
#     mieter(mieter_id: ID!): Mieter!
#     mieterListe(suchparameter: Suchparameter): list[Mieter!]!
# }


_repo: Final = MieterRepository()
_service: MieterService = MieterService(repo=_repo)
_user_service: UserService = UserService()
_write_service: MieterWriteService = MieterWriteService(
    repo=_repo,
    user_service=_user_service,
)
_token_service: Final = TokenService()


@strawberry.type  # vgl. @dataclass
class Query:
    """Queries, um Mieterdaten zu lesen."""

    @strawberry.field
    def mieter(self, mieter_id: strawberry.ID, info: Info) -> MieterDTO | None:
        """Daten zu einem Mieter lesen.

        :param mieter_id: ID des gesuchten Mieters
        :return: Gesuchter Mieter
        :rtype: MieterDTO
        :raises NotFoundError: Falls kein Mieter gefunden wurde, wird zu GraphQLError
        """
        logger.debug("mieter_id={}", mieter_id)

        request: Final[Request] = info.context.get("request")
        user: Final = _token_service.get_user_from_request(request=request)
        if user is None:
            return None

        try:
            mieter_dto: Final = _service.find_by_id(
                mieter_id=int(mieter_id),
                user=user,
            )
        except NotFoundError:
            return None
        logger.debug("{}", mieter_dto)
        return mieter_dto

    @strawberry.field
    def mieter_liste(
        self,
        suchparameter: Suchparameter | None,
        info: Info,
    ) -> Sequence[MieterDTO]:
        """Mieter anhand von Suchparameter suchen.

        :param suchparameter: nachname, email usw.
        :return: Die gefundenen Mieter
        :rtype: list[MieterDTO]
        :raises NotFoundError: Falls kein Mieter gefunden wurde, wird zu GraphQLError
        """
        logger.debug("suchparameter={}", suchparameter)

        request: Final[Request] = info.context["request"]
        user: Final = _token_service.get_user_from_request(request)
        if user is None or Role.ADMIN not in user.roles:
            return []

        suchparameter_filtered = (
            None
            if suchparameter is None
            else MieterSuchparameter(
                email=suchparameter.email,
                nachname=suchparameter.nachname,
            )
        )
        logger.debug("suchparameter_filtered={}", suchparameter_filtered)

        pageable: Final = Pageable.create(size=str(0))
        try:
            mieter_dto: Final = _service.find(
                suchparameter=suchparameter_filtered,
                pageable=pageable,
            )
        except NotFoundError:
            return []
        logger.debug("{}", mieter_dto)
        return mieter_dto.content


@strawberry.type
class Mutation:
    """Mutations, um Mieterdaten anzulegen, zu ändern oder zu löschen."""

    @strawberry.mutation
    def create(self, mieter_input: MieterInput) -> CreatePayload:
        """Einen neuen Mieter anlegen.

        :param mieter_input: Daten des neuen Mieters
        :return: ID des neuen Mieters
        :rtype: CreatePayload
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        """
        logger.debug("mieter_input={}", mieter_input)

        # Dictionary mit Pydantic validieren
        mieter_model: Final = MieterModel.model_validate(asdict(mieter_input))

        mieter_dto: Final = _write_service.create(mieter=mieter_model.to_mieter())
        payload: Final = CreatePayload(id=mieter_dto.id)

        logger.debug("{}", payload)
        return payload

    # Mutation, weil evtl. der Login-Zeitpunkt gespeichert wird
    @strawberry.mutation
    def login(self, username: str, password: str) -> LoginResult:
        """Einen Token zu Benutzername und Passwort ermitteln.

        :param username: Benutzername
        :param password: Passwort
        :rtype: LoginResult
        """
        logger.debug("username={}, password={}", username, password)
        token_mapping = _token_service.token(username=username, password=password)

        token = token_mapping["access_token"]
        user = _token_service.get_user_from_token(token)
        # List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
        roles: Final = [role.value for role in user.roles]
        return LoginResult(token=token, expiresIn="1d", roles=roles)


schema: Final = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    # https://strawberry.rocks/docs/extensions/pydantic_error_extension
    extensions=[
        PydanticErrorExtension,
    ],
)


Context = dict[str, Request]


# Dependency Injection: Request von FastAPI weiterreichen an den Kontext von Strawberry
def get_context(request: Request) -> Context:
    return {"request": request}


# https://strawberry.rocks/docs/integrations/fastapi
graphql_router: Final = GraphQLRouter[Context](
    schema,
    context_getter=get_context,
    graphql_ide=graphql_ide,
)
