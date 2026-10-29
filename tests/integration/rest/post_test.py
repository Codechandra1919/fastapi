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

"""Tests für POST."""

from http import HTTPStatus
from re import search
from typing import Final

import pytest
from common_api_test import certificate_path, rest_url, timeout
from requests import post

token: str | None


@pytest.mark.rest
@pytest.mark.post_request
@pytest.mark.post_request_success
def test_post() -> None:
    # arrange
    neuer_mieter: Final = {
        "vorname": "Vorname",
        "nachname": "Nachnamerest",
        "email": "testrest@rest.de",
        "telefonnummer": "+49 111 1111111",
        "geburtsdatum": "2022-02-01",
        "mietvertrag": {"seiten_anz": 9, "kaution": "999.99"},
        "mietrechnungen": [{"betrag": "999.99", "waehrung": "EUR"}],
        "username": "testrest",
    }
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neuer_mieter,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.CREATED
    location: Final = response.headers.get("Location")
    assert location is not None
    int_pattern: Final = "/[1-9][0-9]*$"
    assert search(int_pattern, location) is not None
    assert not response.text


@pytest.mark.rest
@pytest.mark.post_request
def test_post_invalid() -> None:
    # arrange
    neuer_mieter_invalid: Final = {
        "vorname": "falscher_vorname",
        "nachname": "falscher_nachname",
        "email": "falsche_email@",
        "telefonnummer": "+49 111 1111111",
        "geburtsdatum": "2022-02-01",
        "mietvertrag": {"seiten_anz": 0, "kaution": "999.99"},
        "mietrechnungen": [{"betrag": "222.2", "waehrung": "EURO"}],
        "username": "testrestinvalid",
    }
    headers = {"Content-Type": "application/json"}

    # act
    try:
        response: Final = post(
            rest_url,
            json=neuer_mieter_invalid,
            headers=headers,
            timeout=timeout,
            verify=certificate_path,
        )
    except BaseException as exc:
        raise RuntimeError("Fehler bei POST") from exc

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    body = response.text
    assert "nachname" in body
    assert "email" in body
    assert "mietvertrag" in body
    assert "mietrechnungen" in body
    assert "seiten_anz" in body


@pytest.mark.rest
@pytest.mark.post_request
def test_post_email_exists() -> None:
    # arrange
    email_exists: Final = "alice@acme.de"
    neuer_mieter: Final = {
        "vorname": "Vorname",
        "nachname": "Nachnamerest",
        "email": email_exists,
        "telefonnummer": "+49 111 1111111",
        "geburtsdatum": "2022-02-01",
        "mietvertrag": {"seiten_anz": 9, "kaution": "999.99"},
        "mietrechnungen": [{"betrag": "999.99", "waehrung": "EUR"}],
        "username": "emailexists",
    }
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=neuer_mieter,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert email_exists in response.text


@pytest.mark.rest
@pytest.mark.post_request
def test_post_invalid_json() -> None:
    # arrange
    json_invalid: Final = '{"nachname" "Nachname"}'
    headers = {"Content-Type": "application/json"}

    # act
    response: Final = post(
        rest_url,
        json=json_invalid,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "should be a valid dictionary" in response.text
