# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from types import SimpleNamespace
from typing import cast

import pytest

from superset.constants import PASSWORD_MASK
from superset.databases.ssh_tunnel.models import SSHTunnel
from superset.utils.ssh_tunnel import (
    get_default_port,
    mask_password_info,
    unmask_password_info,
)


def test_mask_password_info_masks_present_secret_keys() -> None:
    tunnel = {
        "password": "secret",
        "private_key": "a-key",
        "private_key_password": "a-key-password",
        "server_address": "localhost",
    }

    result = mask_password_info(dict(tunnel))

    assert result["password"] == PASSWORD_MASK
    assert result["private_key"] == PASSWORD_MASK
    assert result["private_key_password"] == PASSWORD_MASK
    assert result["server_address"] == "localhost"


def test_mask_password_info_ignores_absent_secret_keys() -> None:
    result = mask_password_info({"server_address": "localhost"})

    assert result == {"server_address": "localhost"}


def test_unmask_password_info_restores_masked_values_from_model() -> None:
    model = SimpleNamespace(
        password="real-password",  # noqa: S106
        private_key="real-key",
        private_key_password="real-key-password",  # noqa: S106
    )
    tunnel = {
        "password": PASSWORD_MASK,
        "private_key": "left-untouched",
    }

    result = unmask_password_info(dict(tunnel), cast(SSHTunnel, model))

    assert result["password"] == "real-password"  # noqa: S105
    assert result["private_key"] == "left-untouched"


@pytest.mark.parametrize(
    "backend,expected",
    [
        ("postgresql", 5432),
        ("mysql", 3306),
        ("oracle", 1521),
        ("mssql", 1433),
        ("unknown-backend", None),
    ],
)
def test_get_default_port(backend: str, expected: int | None) -> None:
    assert get_default_port(backend) == expected
