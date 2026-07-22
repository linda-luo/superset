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
import pytest
from werkzeug.routing import Map

from superset.tags.models import ObjectType
from superset.utils.url_map_converters import ObjectTypeConverter, RegexConverter


def test_regex_converter_uses_first_item_as_regex() -> None:
    converter = RegexConverter(Map(), r"\d+", "ignored")  # type: ignore[arg-type]

    assert converter.regex == r"\d+"


def test_object_type_converter_to_python_resolves_enum() -> None:
    converter = ObjectTypeConverter(Map())

    assert converter.to_python("dashboard") is ObjectType.dashboard
    assert converter.to_python("chart") is ObjectType.chart


def test_object_type_converter_to_python_invalid_raises() -> None:
    converter = ObjectTypeConverter(Map())

    with pytest.raises(KeyError):
        converter.to_python("not_a_real_type")


def test_object_type_converter_to_url_returns_name() -> None:
    converter = ObjectTypeConverter(Map())

    assert converter.to_url(ObjectType.dataset) == "dataset"
