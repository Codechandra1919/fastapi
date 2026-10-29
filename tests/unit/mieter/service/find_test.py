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

"""Unit-Tests für find() von MieterReadService."""

from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
lazy from pytest_mock import MockerFixture

from mieter.entity import Mieter, Mietvertrag
from mieter.repository import MieterSuchparameter, Pageable
from mieter.service import NotFoundError

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
@pytest.mark.unit_find
def test_find_by_nachname(mieter_service, session_mock) -> None:
    # Arrange
    nachname = "Mocktest"
    mieter_id = 1
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
        email="mock@email.test",
        telefonnummer="+49 111 1111111",
        geburtsdatum=date(2022, 2, 1),
        username="mocktest",
        mietvertrag=mietvertrag_mock,
        mietrechnungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )
    suchparameter = MieterSuchparameter(nachname=nachname)
    pageable = Pageable(size=5, number=0)
    # session.scalars(select(Mieter)...).all()
    session_mock.scalars.return_value.unique.return_value.all.return_value = [
        mieter_mock
    ]
    session_mock.execute.return_value.scalar.return_value = 1

    # Act
    mieter_slice = mieter_service.find(
        suchparameter=suchparameter,
        pageable=pageable,
    )

    # Assert
    assert len(mieter_slice.content) == 1
    assert mieter_slice.content[0].nachname == nachname


@pytest.mark.unit
@pytest.mark.unit_find
def test_find_by_nachname_not_found(mieter_service, session_mock) -> None:
    # Arrange
    nachname = "Notfound"
    suchparameter = MieterSuchparameter(nachname=nachname)
    pageable = Pageable(size=5, number=0)
    # session.scalars(select(Mieter)...).all()
    session_mock.scalars.return_value.unique.return_value.all.return_value = []
    session_mock.execute.return_value.scalar.return_value = 0

    # Act
    with pytest.raises(NotFoundError) as err:
        mieter_service.find(suchparameter=suchparameter, pageable=pageable)

    # Assert
    assert err.type == NotFoundError
    assert str(err.value) == "Not Found"  # super().__init__("Not Found")
    assert err.value.suchparameter is not None
    assert err.value.suchparameter.nachname == nachname  # pyright: ignore[reportOptionalMemberAccess]


@pytest.mark.unit
@pytest.mark.unit_find
def test_find_by_email(mieter_service, session_mock) -> None:
    # Arrange
    email = "mock@email.test"
    mieter_id = 1
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
        nachname="Mocktest",
        email=email,
        telefonnummer="+49 111 1111111",
        geburtsdatum=date(2022, 2, 1),
        username="mocktest",
        mietvertrag=mietvertrag_mock,
        mietrechnungen=[],
        erzeugt=datetime.now(tz=timezone),
        aktualisiert=datetime.now(tz=timezone),
    )
    suchparameter = MieterSuchparameter(email=email)
    pageable = Pageable(size=5, number=0)
    # session.scalar(select(Mieter)...)
    session_mock.scalar.return_value = mieter_mock

    # Act
    mieter_slice = mieter_service.find(
        suchparameter=suchparameter,
        pageable=pageable,
    )

    # Assert
    assert len(mieter_slice.content) == 1
    assert mieter_slice.content[0].email == email


@pytest.mark.unit
@pytest.mark.unit_find
def test_find_by_email_not_found(mieter_service, session_mock) -> None:
    # Arrange
    email = "not@found.mock"
    suchparameter = MieterSuchparameter(email=email)
    pageable = Pageable(size=5, number=0)
    # session.scalar(select(Mieter)...)
    session_mock.scalar.return_value = None

    # Act
    with pytest.raises(NotFoundError) as err:
        mieter_service.find(suchparameter=suchparameter, pageable=pageable)

    # Assert
    assert str(err.value) == "Not Found"  # super().__init__("Not Found")
    assert err.value.suchparameter is not None
    assert err.value.suchparameter.email == email  # pyright: ignore[reportOptionalMemberAccess]
