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

"""Tests für PUT."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, login, rest_url, timeout
from requests import put

EMAIL_UPDATE: Final = "alice@acme.de.put"


@pytest.mark.rest
@pytest.mark.put_request
def test_put() -> None:
    # arrange
    mieter_id: Final = 1003
    if_match: Final = '"0"'
    geaenderter_mieter: Final = {
        "vorname": "Vorname",
        "nachname": "Nachname",
        "email": EMAIL_UPDATE,
        "telefonnummer": "+49 111 1111111",
        "geburtsdatum": "2022-02-01",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{mieter_id}",
        json=geaenderter_mieter,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not response.text


@pytest.mark.rest
@pytest.mark.put_request
def test_put_invalid() -> None:
    # arrange
    mieter_id: Final = 1003
    geaenderter_mieter_invalid: Final = {
        "vorname": "falscher_vorname_put",
        "nachname": "falscher_nachname_put",
        "email": "falsche_email_put@",
        "telefonnummer": "+49 111 1111111",
        "geburtsdatum": "2022-02-01",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "If-Match": '"0"',
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = put(
        f"{rest_url}/{mieter_id}",
        json=geaenderter_mieter_invalid,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    body = response.text
    assert "nachname" in body
    assert "email" in body


@pytest.mark.rest
@pytest.mark.put_request
def test_put_nicht_vorhanden() -> None:
    # arrange
    mieter_id: Final = 999999
    if_match: Final = '"0"'
    geaenderter_mieter: Final = {
        "vorname": "Vorname",
        "nachname": "Nachname",
        "email": EMAIL_UPDATE,
        "telefonnummer": "+49 111 1111111",
        "geburtsdatum": "2022-02-01",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{mieter_id}",
        json=geaenderter_mieter,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.rest
@pytest.mark.put_request
def test_put_email_exists() -> None:
    # arrange
    mieter_id: Final = 1003
    if_match: Final = '"1"'
    email_exists: Final = "alice@acme.de"
    geaenderter_mieter: Final = {
        "vorname": "Vorname",
        "nachname": "Nachname",
        "email": email_exists,
        "telefonnummer": "+49 111 1111111",
        "geburtsdatum": "2022-02-01",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{mieter_id}",
        json=geaenderter_mieter,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert email_exists in response.text


@pytest.mark.rest
@pytest.mark.put_request
def test_put_ohne_versionsnr() -> None:
    # arrange
    mieter_id: Final = 1003
    geaenderter_mieter: Final = {
        "vorname": "Vorname",
        "nachname": "Nachname",
        "email": EMAIL_UPDATE,
        "telefonnummer": "+49 111 1111111",
        "geburtsdatum": "2022-02-01",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = put(
        f"{rest_url}/{mieter_id}",
        json=geaenderter_mieter,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_REQUIRED


@pytest.mark.rest
@pytest.mark.put_request
def test_put_alte_versionsnr() -> None:
    # arrange
    mieter_id: Final = 1003
    if_match: Final = '"-1"'
    geaenderter_mieter: Final = {
        "vorname": "Vorname",
        "nachname": "Nachname",
        "email": EMAIL_UPDATE,
        "telefonnummer": "+49 111 1111111",
        "geburtsdatum": "2022-02-01",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{mieter_id}",
        json=geaenderter_mieter,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED


@pytest.mark.rest
@pytest.mark.put_request
def test_put_ungueltige_versionsnr() -> None:
    # arrange
    mieter_id: Final = 1003
    if_match: Final = '"xy"'
    geaenderter_mieter: Final = {
        "vorname": "Vorname",
        "nachname": "Nachname",
        "email": EMAIL_UPDATE,
        "telefonnummer": "+49 111 1111111",
        "geburtsdatum": "2022-02-01",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{mieter_id}",
        json=geaenderter_mieter,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED
    assert not response.text


@pytest.mark.rest
@pytest.mark.put_request
def test_put_versionsnr_ohne_quotes() -> None:
    # arrange
    mieter_id: Final = 1003
    if_match: Final = "0"
    geaenderter_mieter: Final = {
        "vorname": "Vorname",
        "nachname": "Nachname",
        "email": EMAIL_UPDATE,
        "telefonnummer": "+49 111 1111111",
        "geburtsdatum": "2022-02-01",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{mieter_id}",
        json=geaenderter_mieter,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED
