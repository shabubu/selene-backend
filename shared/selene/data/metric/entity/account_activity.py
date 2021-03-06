# Mycroft Server - Backend
# Copyright (C) 2020 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""Defines data entities related to account activity metrics."""
from dataclasses import dataclass


@dataclass
class AccountActivity:
    """Data class representing a row on the account_activity table."""

    accounts: int
    accounts_added: int
    accounts_deleted: int
    accounts_active: int
    members: int
    members_added: int
    members_expired: int
    members_active: int
    open_dataset: int
    open_dataset_added: int
    open_dataset_deleted: int
    open_dataset_active: int
