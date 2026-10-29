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

"""Schema für GraphQL."""

lazy from datetime import date
lazy from decimal import Decimal

import strawberry

__all__ = [
    "CreatePayload",
    "MieterInput",
    "MietrechnungInput",
    "MietvertragInput",
    "Suchparameter",
]

# SDL (schema definition language):
# type Mieter {
#     nachname: String!
# }
# type Query {
#     mieter(mieter_id: ID!): Mieter!
#     mieterListe(input: Suchparameter): [Mieter!]
# }
# type Mutation {
#     create(mieter_input: MieterInput!): CreatePayload!
# }


@strawberry.input
class Suchparameter:
    """Suchparameter für die Suche nach Mietern."""

    nachname: str | None = None
    """Nachname als Suchkriterium."""

    email: str | None = None
    """Emailadresse als Suchkriterium."""


@strawberry.input
class MietvertragInput:
    """Mietvertrag zu einem neuen Mieter."""

    seiten_anz: int
    """Anzahl der Seiten des Mietvertrags."""

    kaution: Decimal
    """Kaution des Mietvertrags."""


@strawberry.input
class MietrechnungInput:
    """Mietrechnung zu einem neuen Mieter."""

    betrag: Decimal
    """Betrag."""

    waehrung: str
    """Währung als 3-stellige Zeichenkette."""


@strawberry.input
class MieterInput:
    """Daten für einen neuen Mieter."""

    vorname: str
    """Vorname."""

    nachname: str
    """Nachname."""

    email: str
    """Emailadresse."""

    telefonnummer: str
    """Optionale Telefonnummer."""

    geburtsdatum: date
    """Optionales Geburtsdatum."""

    username: str
    """Benutzername für den Login."""

    mietvertrag: MietvertragInput
    """Mietvertrag."""

    mietrechnungen: list[MietrechnungInput]
    """Mietrechnungen."""


@strawberry.type
class CreatePayload:
    """Resultat-Typ, wenn ein neuer Mieter angelegt wurde."""

    id: int
    """ID des neu angelegten Mieters."""


@strawberry.type
class LoginResult:
    """Resultat-Typ, wenn ein Login erfolgreich war."""

    token: str
    """Token des eingeloggten Users."""

    expiresIn: str  # ruff: ignore[mixed-case-variable-in-class-scope]  # NOSONAR
    """Gültigkeitsdauer des Tokens."""

    roles: list[str]
    """Rollen des eingeloggten Users."""
