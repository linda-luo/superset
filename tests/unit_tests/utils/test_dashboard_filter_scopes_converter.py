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
from typing import Any, cast

from superset.models.slice import Slice
from superset.utils import json
from superset.utils.dashboard_filter_scopes_converter import (
    convert_filter_scopes,
    copy_filter_scopes,
)


def _filter_box(slice_id: int, params: dict[str, Any]) -> Slice:
    return cast(Slice, SimpleNamespace(id=slice_id, params=json.dumps(params)))


def test_convert_filter_scopes_time_filters() -> None:
    box = _filter_box(
        1,
        {
            "date_filter": True,
            "show_sqla_time_column": True,
            "show_sqla_time_granularity": True,
        },
    )

    result = convert_filter_scopes({}, [box])

    assert set(result[1]) == {"__time_range", "__time_col", "__time_grain"}
    assert result[1]["__time_range"] == {"scope": ["ROOT_ID"], "immune": []}


def test_convert_filter_scopes_filter_configs_columns() -> None:
    box = _filter_box(
        2,
        {"filter_configs": [{"column": "gender"}, {"column": "name"}]},
    )

    result = convert_filter_scopes({}, [box])

    assert set(result[2]) == {"gender", "name"}


def test_convert_filter_scopes_immune_by_slice_id() -> None:
    box = _filter_box(3, {"date_filter": True})

    result = convert_filter_scopes({"filter_immune_slices": [99]}, [box])

    assert result[3]["__time_range"]["immune"] == [99]


def test_convert_filter_scopes_immune_by_column() -> None:
    box = _filter_box(4, {"filter_configs": [{"column": "gender"}]})

    result = convert_filter_scopes(
        {"filter_immune_slice_fields": {"4": ["gender"]}}, [box]
    )

    assert result[4]["gender"]["immune"] == [4]


def test_convert_filter_scopes_skips_invalid_column() -> None:
    box = _filter_box(5, {"filter_configs": [{"not_a_column": "x"}]})

    result = convert_filter_scopes({}, [box])

    assert result == {}


def test_convert_filter_scopes_skips_boxes_without_filters() -> None:
    box = _filter_box(6, {})

    result = convert_filter_scopes({}, [box])

    assert result == {}


def test_copy_filter_scopes_remaps_ids() -> None:
    old_scopes: dict[int, dict[str, dict[str, Any]]] = {
        1: {"gender": {"scope": ["ROOT_ID"], "immune": [2, 3]}}
    }

    result = copy_filter_scopes({1: 10, 2: 20, 3: 30}, old_scopes)

    assert "10" in result
    assert result["10"]["gender"]["immune"] == [20, 30]


def test_copy_filter_scopes_drops_unmapped_filter_and_immune_ids() -> None:
    old_scopes: dict[int, dict[str, dict[str, Any]]] = {
        1: {"gender": {"scope": ["ROOT_ID"], "immune": [2, 3]}},
        7: {"name": {"scope": ["ROOT_ID"], "immune": []}},
    }

    result = copy_filter_scopes({1: 10}, old_scopes)

    assert set(result) == {"10"}
    assert result["10"]["gender"]["immune"] == []
