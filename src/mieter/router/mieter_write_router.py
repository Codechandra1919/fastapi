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

"""MieterWriteRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status
from loguru import logger

from mieter.problem_details import ProblemDetails
from mieter.router.constants import IF_MATCH, IF_MATCH_MIN_LEN
from mieter.router.dependencies import get_write_service
from mieter.security import Role, RolesRequired
from mieter.service import send_mail
lazy from mieter.router.mieter_model import MieterModel
lazy from mieter.router.mieter_update_model import MieterUpdateModel
lazy from mieter.service import MieterWriteService

__all__ = ["mieter_write_router"]


mieter_write_router: Final = APIRouter(tags=["Schreiben"])


@mieter_write_router.post("")
def post(
    mieter_model: MieterModel,
    request: Request,
    background_tasks: BackgroundTasks,
    service: Annotated[MieterWriteService, Depends(get_write_service)],
) -> Response:
    """POST-Request, um einen neuen Mieter anzulegen.

    :param mieter_model: Mieterdaten als Pydantic-Model
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit der Request-URL
    :param background_tasks: Hintergrundtask für den Mailversand
    :param service: Injizierter Service für Geschäftslogik
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises EmailExistsError: Falls die Emailadresse bereits existiert
    """
    logger.debug("mieter_model={}", mieter_model)
    mieter_dto: Final = service.create(
        mieter=mieter_model.to_mieter(),
    )
    logger.debug("mieter_dto={}", mieter_dto)

    background_tasks.add_task(send_mail, mieter_dto)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{mieter_dto.id}"},
        background=background_tasks,
    )


@mieter_write_router.put(
    "/{mieter_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.MIETER]))],
)
def put(
    mieter_id: int,
    mieter_update_model: MieterUpdateModel,
    request: Request,
    service: Annotated[MieterWriteService, Depends(get_write_service)],
) -> Response:
    """PUT-Request, um einen Mieter zu aktualisieren.

    :param mieter_id: ID des zu aktualisierenden Mieters als Pfadparameter
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit If-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises EmailExistsError: Falls die neue Emailadresse bereits existiert
    :raises NotFoundError: Falls zur id kein Mieter existiert
    :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
    """
    if_match_value: Final = request.headers.get(IF_MATCH)
    logger.debug(
        "mieter_id={}, if_match={}, mieter_update_model={}",
        mieter_id,
        if_match_value,
        mieter_update_model,
    )

    if if_match_value is None:
        return ProblemDetails.create(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
        ).to_response()

    if (
        len(if_match_value) < IF_MATCH_MIN_LEN
        or not if_match_value.startswith('"')
        or not if_match_value.endswith('"')
    ):
        return ProblemDetails.create(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        ).to_response()

    version: Final = if_match_value[1:-1]
    try:
        version_int: Final = int(version)
    except ValueError:
        return Response(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        )

    mieter: Final = mieter_update_model.to_mieter()
    mieter_modified: Final = service.update(
        mieter=mieter,
        mieter_id=mieter_id,
        version=version_int,
    )
    logger.debug("mieter_modified={}", mieter_modified)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": f'"{mieter_modified.version}"'},
    )


@mieter_write_router.delete(
    "/{mieter_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.MIETER]))],
)
def delete_by_id(
    mieter_id: int,
    service: Annotated[MieterWriteService, Depends(get_write_service)],
) -> Response:
    """DELETE-Request, um einen Mieter anhand seiner ID zu löschen.

    :param mieter_id: ID des zu löschenden Mieters
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    """
    logger.debug("mieter_id={}", mieter_id)
    service.delete_by_id(mieter_id=mieter_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
