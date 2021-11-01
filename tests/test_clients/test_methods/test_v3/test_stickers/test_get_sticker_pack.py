import uuid

import pytest

from botx.clients.methods.v3.stickers.sticker_pack import GetStickerPack
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_get_sticker_pack(client, requests_client):
    sticker_pack_name = "Test sticker pack"

    method = GetStickerPack(pack_id=uuid.uuid4(), host="example.com")
    request = requests_client.build_request(method)
    response = await callable_to_coroutine(requests_client.execute, request)

    sticker_pack = await callable_to_coroutine(
        requests_client.process_response,
        method,
        response,
    )

    assert sticker_pack.name == sticker_pack_name
