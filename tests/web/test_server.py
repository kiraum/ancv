from contextlib import nullcontext as does_not_raise
from datetime import timedelta
from http import HTTPStatus
from typing import Any, ContextManager

import pytest
from aiohttp.client import ClientResponse
from aiohttp.web import Application

from ancv.web.server import server_timing_header


@pytest.mark.filterwarnings("ignore:Request.message is deprecated")  # No idea...
@pytest.mark.filterwarnings("ignore:Exception ignored in")  # No idea...
@pytest.mark.asyncio
class TestApiHandler:
    @pytest.mark.parametrize(
        ["user_agent", "expected_http_code"],
        [
            ("curl", HTTPStatus.OK),
            ("powershell", HTTPStatus.OK),
            ("wget", HTTPStatus.OK),
            ("Some Browser/1.0", HTTPStatus.FOUND),
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
                HTTPStatus.FOUND,
            ),
        ],
    )
    async def test_root_endpoint(
        self,
        user_agent: str,
        expected_http_code: HTTPStatus,
        aiohttp_client: Any,
        api_client_app: Application,
        event_loop: Any,
    ) -> None:
        client = await aiohttp_client(api_client_app)

        resp: ClientResponse = await client.get(
            "/",
            headers={"User-Agent": user_agent},
            allow_redirects=False,  # So we can test the redirect
        )
        assert resp.status == expected_http_code

    @pytest.mark.parametrize(
        ["username", "expected_http_code"],
        [
            ("alexpovel", HTTPStatus.OK),
            (
                "this-user-cannot-exist-because-its-username-is-way-too-long",
                HTTPStatus.NOT_FOUND,
            ),
        ],
    )
    async def test_username_endpoint(
        self,
        username: str,
        expected_http_code: HTTPStatus,
        aiohttp_client: Any,
        api_client_app: Application,
        event_loop: Any,
    ) -> None:
        client = await aiohttp_client(api_client_app)

        resp = await client.get(f"/{username}")
        assert resp.status == expected_http_code

    @pytest.mark.parametrize(
        ["username", "expected_contained_text"],
        [
            ("alexpovel", "Experience"),
        ],
    )
    async def test_return_content(
        self,
        username: str,
        expected_contained_text: str,
        aiohttp_client: Any,
        api_client_app: Application,
        event_loop: Any,
    ) -> None:
        client = await aiohttp_client(api_client_app)

        resp = await client.get(f"/{username}")

        text = await resp.text()
        assert expected_contained_text in text


@pytest.mark.filterwarnings("ignore:Request.message is deprecated")  # No idea...
@pytest.mark.filterwarnings("ignore:Exception ignored in")  # No idea...
@pytest.mark.asyncio
class TestFileHandler:
    @pytest.mark.parametrize(
        ["expected_http_code", "expected_str_content"],
        [
            (HTTPStatus.OK, "John Doe"),
            (HTTPStatus.OK, "Experience"),
            (HTTPStatus.OK, "Skills"),
        ],
    )
    async def test_root_endpoint(
        self,
        expected_http_code: HTTPStatus,
        expected_str_content: str,
        aiohttp_client: Any,
        file_handler_app: Application,
        event_loop: Any,
    ) -> None:
        client = await aiohttp_client(file_handler_app)

        resp: ClientResponse = await client.get("/")
        assert resp.status == expected_http_code
        assert expected_str_content in await resp.text()


@pytest.mark.parametrize(
    ["timings", "expected", "expectation"],
    [
        (None, None, pytest.raises(AttributeError)),
        (
            {},
            "",
            does_not_raise(),
        ),
        (
            {
                "Spaces Work As Well": timedelta(seconds=0.1),
            },
            "Spaces-Work-As-Well;dur=100",
            does_not_raise(),
        ),
        (
            {
                "A": timedelta(seconds=0),
            },
            "A;dur=0",
            does_not_raise(),
        ),
        (
            {
                "A": timedelta(seconds=0.1),
            },
            "A;dur=100",
            does_not_raise(),
        ),
        (
            {
                "A": timedelta(seconds=1),
                "B": timedelta(seconds=2),
            },
            "A;dur=1000, B;dur=2000",
            does_not_raise(),
        ),
        (
            {
                "A": timedelta(seconds=1),
                "B": timedelta(seconds=2),
                "C": timedelta(seconds=3),
                "D": timedelta(seconds=4),
                "E": timedelta(seconds=5),
                "F": timedelta(seconds=6),
                "G": timedelta(seconds=7),
                "H": timedelta(seconds=8),
                "I": timedelta(seconds=9),
                "J": timedelta(seconds=10),
                "K": timedelta(seconds=11),
                "L": timedelta(seconds=12),
                "M": timedelta(seconds=13),
                "N": timedelta(seconds=14),
                "O": timedelta(seconds=15),
                "P": timedelta(seconds=16),
                "Q": timedelta(seconds=17),
                "R": timedelta(seconds=18),
                "S": timedelta(seconds=19),
                "T": timedelta(seconds=20),
                "U": timedelta(seconds=21),
                "V": timedelta(seconds=22),
                "W": timedelta(seconds=23),
                "X": timedelta(seconds=24),
                "Y": timedelta(seconds=25),
                "Z": timedelta(seconds=26),
            },
            "A;dur=1000, B;dur=2000, C;dur=3000, D;dur=4000, E;dur=5000, F;dur=6000, G;dur=7000, H;dur=8000, I;dur=9000, J;dur=10000, K;dur=11000, L;dur=12000, M;dur=13000, N;dur=14000, O;dur=15000, P;dur=16000, Q;dur=17000, R;dur=18000, S;dur=19000, T;dur=20000, U;dur=21000, V;dur=22000, W;dur=23000, X;dur=24000, Y;dur=25000, Z;dur=26000",
            does_not_raise(),
        ),
    ],
)
def test_server_timing_header(
    timings: dict[str, timedelta],
    expected: str,
    expectation: ContextManager,
) -> None:
    with expectation:
        assert server_timing_header(timings) == expected
