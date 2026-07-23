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
from unittest.mock import MagicMock, patch

from superset.common.utils.query_cache_manager import QueryCacheManager
from superset.constants import CacheRegion


@patch("superset.common.utils.query_cache_manager._cache")
def test_get_fails_open_on_cache_backend_error(mock_cache: MagicMock) -> None:
    """
    A backend error while reading the query cache (e.g. a Redis
    connection/timeout error) must be treated as a cache miss so that the
    request can fall through to a live query, rather than propagating up and
    turning every chart/dashboard load into a 500.
    """
    backend = MagicMock()
    backend.get.side_effect = ConnectionError("backend down")
    mock_cache.__getitem__.return_value = backend

    query_cache = QueryCacheManager.get("some-key", region=CacheRegion.DATA)

    backend.get.assert_called_once_with("some-key")
    assert query_cache.is_loaded is False
    assert query_cache.cache_value is None


@patch("superset.common.utils.query_cache_manager._cache")
def test_get_fails_open_raises_cache_load_error_when_force_cached(
    mock_cache: MagicMock,
) -> None:
    """
    When ``force_cached`` is set and the backend errors, the value is treated
    as missing and ``CacheLoadError`` is raised (same as an ordinary miss),
    never the raw backend exception.
    """
    from superset.exceptions import CacheLoadError

    backend = MagicMock()
    backend.get.side_effect = TimeoutError("backend timeout")
    mock_cache.__getitem__.return_value = backend

    try:
        QueryCacheManager.get("some-key", region=CacheRegion.DATA, force_cached=True)
    except CacheLoadError:
        pass
    else:
        raise AssertionError("expected CacheLoadError to be raised")
