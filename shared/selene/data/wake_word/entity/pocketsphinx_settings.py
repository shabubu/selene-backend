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

from dataclasses import dataclass


@dataclass
class PocketsphinxSettings(object):
    id: str
    sample_rate: int
    channels: int
    pronunciation: str
    threshold: str
    threshold_multiplier: float
    dynamic_energy_ratio: float
    account_id: str = None