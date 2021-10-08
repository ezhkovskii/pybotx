from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx

from botx import BotAccount
from botx.bot.bot_accounts_storage import BotAccountsStorage
from botx.client.authorized_botx_method import AuthorizedBotXMethod
from tests.client.test_botx_method import (
    BotXAPIFooBarRequestPayload,
    BotXAPIFooBarResponsePayload,
)


class FooBarMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPIFooBarRequestPayload,
    ) -> BotXAPIFooBarResponsePayload:
        path = "/foo/bar"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._extract_api_model(BotXAPIFooBarResponsePayload, response)


@respx.mock
@pytest.mark.asyncio
async def test__authorized_botx_method__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    bot_signature: str,
    bot_account: BotAccount,
    sync_id: UUID,
) -> None:
    # - Arrange -
    token_endpoint = respx.get(
        f"https://{host}/api/v2/botx/bots/{bot_id}/token",
        params={"signature": bot_signature},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": "token",
            },
        ),
    )

    foo_bar_endpoint = respx.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"sync_id": str(sync_id)},
            },
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    botx_api_foo_bar = await method.execute(payload)

    # - Assert -
    assert botx_api_foo_bar.to_domain() == sync_id
    assert token_endpoint.called
    assert foo_bar_endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__authorized_botx_method__with_prepared_token(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    prepared_bot_accounts_storage: BotAccountsStorage,
    sync_id: UUID,
) -> None:
    # - Arrange -
    endpoint = respx.post(
        f"https://{host}/foo/bar",
        json={"baz": 1},
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {"sync_id": str(sync_id)},
            },
        ),
    )

    method = FooBarMethod(
        bot_id,
        httpx_client,
        prepared_bot_accounts_storage,
    )

    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    botx_api_foo_bar = await method.execute(payload)

    # - Assert -
    assert botx_api_foo_bar.to_domain() == sync_id
    assert endpoint.called
