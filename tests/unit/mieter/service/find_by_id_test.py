# ruff: file-ignore[hardcoded-password-func-arg]
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

"""Unit-Tests für find_by_id() von MieterService."""

from dataclasses import asdict
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
lazy from pytest_mock import MockerFixture

from mieter.entity import Mieter, Mietvertrag
from mieter.security import Role, User
from mieter.service import ForbiddenError, MieterDTO, MieterService, NotFoundError

timezone = ZoneInfo("Europe/Berlin")


@pytest.fixture
def session_mock(mocker: MockerFixture):
    session = mocker.Mock()
    # Patching von "with Session() as session:" in mieter_service.py
    mocker.patch(
        "mieter.service.mieter_service.Session",
        return_value=mocker.MagicMock(
            __enter__=lambda self: session,
            __exit__=lambda self, exc_type, exc, tb: None,
        ),
    )
    return session


@pytest.mark.unit
@pytest.mark.unit_find_by_id
def test_find_by_id(mieter_service, session_mock) -> None:
    # Arrange
    mieter_id = 1
    username = "mocktest"
    email = "mock@email.test"
    nachname = "Mocktest"

    user_mock = User(
        username=username,
        email=email,
        nachname=nachname,
        vorname=nachname,
        roles=[Role.ADMIN],
        password="mockpass",
    )
    mietvertrag_mock = Mietvertrag(
        id=None,
        seiten_anz=9,
        kaution=Decimal("999.99"),
        mieter_id=None,
        mieter=None,
    )
    mieter_mock = Mieter(
        id=mieter_id,
        vorname="VornameMock",
        nachname=nachname,
        email=email,
        telefonnummer="+49 111 1111111",
        geburtsdatum=date(2022, 2, 1),
        username=username,
        mietvertrag=mietvertrag_mock,
        mietrechnungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )
    mieter_dto_mock = MieterDTO.from_mieter(mieter_mock)
    # session.scalar(select(Mieter)...)
    session_mock.scalar.return_value = mieter_mock

    # Act
    mieter_dto = mieter_service.find_by_id(mieter_id=mieter_id, user=user_mock)

    # Assert
    assert asdict(mieter_dto) == asdict(mieter_dto_mock)


@pytest.mark.unit
@pytest.mark.unit_find_by_id
def test_find_by_id_not_found(mieter_service: MieterService, session_mock) -> None:
    # Arrange
    mieter_id = 999
    user_mock = User(
        username="mocktest",
        email="mock@email.test",
        nachname="Mocktest",
        vorname="Mocktest",
        roles=[Role.ADMIN],
        password="mockpass",
    )
    # session.scalar(select(Mieter)...)
    session_mock.scalar.return_value = None

    # Act
    with pytest.raises(NotFoundError) as err:
        mieter_service.find_by_id(mieter_id=mieter_id, user=user_mock)

    # Assert
    assert err.type == NotFoundError
    assert str(err.value) == "Not Found"  # super().__init__("Not Found")
    assert err.value.mieter_id == mieter_id


@pytest.mark.unit
@pytest.mark.unit_find_by_id
def test_find_by_id_not_found_not_admin(
    mieter_service: MieterService,
    session_mock,
) -> None:
    # Arrange
    mieter_id = 999
    user_mock = User(
        username="mocktest",
        email="mock@email.test",
        nachname="Mocktest",
        vorname="Mocktest",
        roles=[],
        password="mockpass",
    )
    # session.scalar(select(Mieter)...)
    session_mock.scalar.return_value = None

    # Act
    with pytest.raises(ForbiddenError) as err:
        mieter_service.find_by_id(mieter_id=mieter_id, user=user_mock)

    # Assert
    assert err.type == ForbiddenError


@pytest.mark.unit
@pytest.mark.unit_find_by_id
def test_find_by_id_not_admin(mieter_service, session_mock) -> None:
    # Arrange
    mieter_id = 1
    username = "mocktest"
    email = "mock@email.test"
    nachname = "Mocktest"

    user_mock = User(
        username=username,
        email=email,
        nachname=nachname,
        vorname=nachname,
        roles=[Role.MIETER],
        password="mockpass",
    )
    mietvertrag_mock = Mietvertrag(
        id=None,
        seiten_anz=9,
        kaution=Decimal("999.99"),
        mieter_id=None,
        mieter=None,
    )
    mieter_mock = Mieter(
        id=mieter_id,
        vorname="VornameMock",
        nachname=nachname,
        email=email,
        telefonnummer="+49 111 1111111",
        geburtsdatum=date(2022, 2, 1),
        username=username,
        mietvertrag=mietvertrag_mock,
        mietrechnungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )
    mieter_dto_mock = MieterDTO.from_mieter(mieter_mock)
    # session.scalar(select(Mieter)...)
    session_mock.scalar.return_value = mieter_mock

    # Act
    mieter_dto = mieter_service.find_by_id(mieter_id=mieter_id, user=user_mock)

    # Assert
    assert asdict(mieter_dto) == asdict(mieter_dto_mock)


@pytest.mark.unit
@pytest.mark.unit_find_by_id
def test_find_by_id_other(mieter_service, session_mock) -> None:
    # Arrange
    mieter_id = 1
    email = "mock@email.test"
    nachname = "Mocktest"

    user_mock = User(
        username="other",
        email=email,
        nachname=nachname,
        vorname=nachname,
        roles=[Role.MIETER],
        password="mockpass",
    )
    mietvertrag_mock = Mietvertrag(
        id=None,
        seiten_anz=9,
        kaution=Decimal("999.99"),
        mieter_id=None,
        mieter=None,
    )
    mieter_mock = Mieter(
        id=mieter_id,
        vorname="VornameMock",
        nachname=nachname,
        email=email,
        telefonnummer="+49 111 1111111",
        geburtsdatum=date(2022, 2, 1),
        username="mocktest",
        mietvertrag=mietvertrag_mock,
        mietrechnungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )
    # session.scalar(select(Mieter)...)
    session_mock.scalar.return_value = mieter_mock

    # Act
    with pytest.raises(ForbiddenError) as err:
        mieter_service.find_by_id(mieter_id=mieter_id, user=user_mock)

    # Assert
    assert err.type == ForbiddenError
