# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Unit-Tests für create() von MieterWriteService."""

from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal
from typing import Final
from zoneinfo import ZoneInfo

import pytest
lazy from pytest_mock import MockerFixture

from mieter.entity import Mieter, Mietvertrag
from mieter.service import EmailExistsError, UsernameExistsError
from mieter.service.exceptions import EmptyUsernameError

timezone = ZoneInfo("Europe/Berlin")


@pytest.fixture
def session_mock(mocker: MockerFixture):
    session = mocker.Mock()
    # Patching von "with Session() as session:" in mieter_write_service.py
    mocker.patch(
        "mieter.service.mieter_write_service.Session",
        return_value=mocker.MagicMock(
            __enter__=lambda self: session,
            __exit__=lambda self, exc_type, exc, tb: None,
        ),
    )
    return session


@pytest.mark.unit
@pytest.mark.unit_create
def test_create(mieter_write_service, session_mock, keycloak_admin_mock) -> None:
    # Arrange
    email = "mock@email.test"
    mietvertrag = Mietvertrag(
        id=None,
        seiten_anz=9,
        kaution=Decimal("999.99"),
        mieter_id=None,
        mieter=None,
    )
    mieter = Mieter(
        id=None,
        vorname="VornameMock",
        nachname="NachnameMock",
        email=email,
        telefonnummer="+49 111 1111111",
        geburtsdatum=date(2022, 2, 1),
        username="mocktest",
        mietvertrag=mietvertrag,
        mietrechnungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )
    mieter_db_mock = deepcopy(mieter)
    generierte_id: Final[int] = 1
    mieter_db_mock.id = generierte_id

    # Patch fuer KeycloakAdmin.get_user_id() und KeycloakAdmin.get_users()
    keycloak_admin_mock.get_user_id.return_value = None
    keycloak_admin_mock.get_users.return_value = []

    # session.scalar(select(func.count()).where(Mieter.email == email)
    session_mock.scalar.return_value = 0
    session_mock.add.return_value = None

    def flush_side_effect(objects=None):
        for obj in objects or []:
            obj.id = generierte_id  # Emulation: generierter PK in session.flush()

    session_mock.flush.side_effect = flush_side_effect

    # Act
    mieter_dto = mieter_write_service.create(mieter=mieter)

    # Assert
    assert mieter_dto.id == generierte_id


@pytest.mark.unit
@pytest.mark.unit_create
def test_create_username_none(mieter_write_service) -> None:
    # Arrange
    mietvertrag = Mietvertrag(
        id=None,
        seiten_anz=9,
        kaution=Decimal("999.99"),
        mieter_id=None,
        mieter=None,
    )
    mieter = Mieter(
        id=None,
        vorname="VornameMock",
        nachname="NachnameMock",
        email="mock@email.test",
        telefonnummer="+49 111 1111111",
        geburtsdatum=date(2022, 2, 1),
        username=None,
        mietvertrag=mietvertrag,
        mietrechnungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )

    # Act
    with pytest.raises(
        expected_exception=EmptyUsernameError,
        match="username ist None oder leer",
    ) as err:
        mieter_write_service.create(mieter=mieter)

    # Assert
    assert err.type is EmptyUsernameError


@pytest.mark.unit
@pytest.mark.unit_create
def test_create_username_exists(mieter_write_service, keycloak_admin_mock) -> None:
    # Arrange
    email = "mock@email.test"
    mietvertrag = Mietvertrag(
        id=None,
        seiten_anz=9,
        kaution=Decimal("999.99"),
        mieter_id=None,
        mieter=None,
    )
    mieter = Mieter(
        id=None,
        vorname="VornameMock",
        nachname="NachnameMock",
        email=email,
        telefonnummer="+49 111 1111111",
        geburtsdatum=date(2022, 2, 1),
        username="mocktest",
        mietvertrag=mietvertrag,
        mietrechnungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )

    # Patch fuer KeycloakAdmin.get_user_id()
    user_id = "12345678-1234-1234-1234-123456789012"
    keycloak_admin_mock.get_user_id.return_value = user_id
    keycloak_admin_mock.get_users.return_value = []

    # Act
    with pytest.raises(UsernameExistsError) as err:
        mieter_write_service.create(mieter=mieter)

    # Assert
    assert err.type is UsernameExistsError


@pytest.mark.unit
@pytest.mark.unit_create
def test_create_email_exists(mieter_write_service, keycloak_admin_mock) -> None:
    # Arrange
    email = "mock@email.test"
    mietvertrag = Mietvertrag(
        id=None,
        seiten_anz=9,
        kaution=Decimal("999.99"),
        mieter_id=None,
        mieter=None,
    )
    mieter = Mieter(
        id=None,
        vorname="VornameMock",
        nachname="NachnameMock",
        email=email,
        telefonnummer="+49 111 1111111",
        geburtsdatum=date(2022, 2, 1),
        username="mocktest",
        mietvertrag=mietvertrag,
        mietrechnungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )

    # Patch fuer KeycloakAdmin.get_users()
    keycloak_admin_mock.get_user_id.return_value = None  # sonst UsernameExistsError
    keycloak_admin_mock.get_users.return_value = [
        {"id": "12345678-1234-1234-1234-123456789012", "email": email},
    ]

    # Act
    with pytest.raises(EmailExistsError) as err:
        mieter_write_service.create(mieter=mieter)

    # Assert
    assert err.type is EmailExistsError
