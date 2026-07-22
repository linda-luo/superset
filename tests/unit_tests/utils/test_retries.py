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
from unittest.mock import Mock

import pytest

from superset.utils.retries import retry_call


def test_retry_call_returns_value_without_retrying() -> None:
    func = Mock(return_value="ok")

    result = retry_call(func, fargs=["a"], fkwargs={"b": 1})

    assert result == "ok"
    func.assert_called_once_with("a", b=1)


def test_retry_call_retries_until_success() -> None:
    attempts = {"count": 0}

    def flaky() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ValueError("boom")
        return "done"

    result = retry_call(flaky, exception=ValueError, max_tries=5, interval=0)

    assert result == "done"
    assert attempts["count"] == 3


def test_retry_call_gives_up_and_reraises_after_max_tries() -> None:
    attempts = {"count": 0}

    def always_fails() -> None:
        attempts["count"] += 1
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        retry_call(always_fails, exception=ValueError, max_tries=3, interval=0)

    assert attempts["count"] == 3


def test_retry_call_does_not_retry_unlisted_exception() -> None:
    attempts = {"count": 0}

    def always_fails() -> None:
        attempts["count"] += 1
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        retry_call(always_fails, exception=KeyError, max_tries=3, interval=0)

    assert attempts["count"] == 1
