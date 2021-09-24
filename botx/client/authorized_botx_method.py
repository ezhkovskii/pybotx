from typing import Any

import httpx

from botx.client.botx_method import BotXMethod
from botx.client.get_token import get_token


class AuthorizedBotXMethod(BotXMethod):
    async def _botx_method_call(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> httpx.Response:
        token = self._credentials_storage.get_token_or_none(self._bot_id)
        if not token:
            token = await get_token(
                self._bot_id,
                self._httpx_client,
                self._credentials_storage,
            )
            self._credentials_storage.set_token(self._bot_id, token)

        headers = kwargs.pop("headers", {})
        headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

        return await super()._botx_method_call(*args, headers=headers, **kwargs)
