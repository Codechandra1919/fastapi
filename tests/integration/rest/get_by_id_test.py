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

"""Tests für GET mit Pfadparameter für die ID."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, login, rest_url, timeout
from requests import get


# in pyproject.toml bei der Table [tool.pytest.ini_options] gibt es das Array "markers"
@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("mieter_id", [2, 0, 1])
def test_get_by_id_admin(mieter_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{mieter_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    id_actual: Final = response_body.get("id")
    assert id_actual is not None
    assert id_actual == mieter_id


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("mieter_id", [-1, 999999])
def test_get_by_id_not_found(mieter_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{mieter_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.rest
@pytest.mark.get_request
def test_get_by_id_mieter() -> None:
    # arrange
    mieter_id: Final = 1
    token: Final = login(username="alice.mueller")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{mieter_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    mieter_id_response: Final = response_body.get("id")
    assert mieter_id_response is not None
    assert mieter_id_response == mieter_id


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("mieter_id", [0, 2])
def test_get_by_id_not_allowed(mieter_id: int) -> None:
    # arrange
    token: Final = login(username="alice.mueller")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{mieter_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("mieter_id", [0, 999999])
def test_get_by_id_not_allowed_not_found(mieter_id: int) -> None:
    # arrange
    token: Final = login(username="alice.mueller")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{mieter_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("mieter_id", [2, 0, 1])
def test_get_by_id_ungueltiger_token(mieter_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}XXX"}

    # act
    response: Final = get(
        f"{rest_url}/{mieter_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("mieter_id", [2, 0, 1])
def test_get_by_id_ohne_token(mieter_id: int) -> None:
    # act
    response: Final = get(
        f"{rest_url}/{mieter_id}",
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize(("mieter_id", "if_none_match"), [(1, '"0"'), (2, '"0"')])
def test_get_by_id_etag(mieter_id: int, if_none_match: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-None-Match": if_none_match,
    }

    # act
    response: Final = get(
        f"{rest_url}/{mieter_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_MODIFIED
    assert not response.text


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize(
    ("mieter_id", "if_none_match"),
    [(2, 'xxx"'), (0, "xxx"), (1, "xxx")],
)
def test_get_by_id_etag_invalid(mieter_id: int, if_none_match: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-None-Match": if_none_match,
    }

    # act
    response: Final = get(
        f"{rest_url}/{mieter_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    id_actual: Final = response_body.get("id")
    assert id_actual is not None
    assert id_actual == mieter_id
