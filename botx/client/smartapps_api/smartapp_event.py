from typing import Any, Dict, List
from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.constants import SMARTAPP_API_VERSION
from botx.missing import Missing, MissingOptional, Undefined
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from botx.models.async_files import APIAsyncFile, File, convert_async_file_from_domain

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPISmartAppEventRequestPayload(UnverifiedPayloadBaseModel):
    ref: MissingOptional[UUID]
    smartapp_id: UUID
    group_chat_id: UUID
    data: Dict[str, Any]
    opts: Missing[Dict[str, Any]]
    smartapp_api_version: int
    async_files: Missing[List[APIAsyncFile]]

    @classmethod
    def from_domain(
        cls,
        ref: MissingOptional[UUID],
        bot_id: UUID,
        chat_id: UUID,
        data: Dict[str, Any],
        opts: Missing[Dict[str, Any]],
        files: Missing[List[File]],
    ) -> "BotXAPISmartAppEventRequestPayload":
        api_async_files: Missing[List[APIAsyncFile]] = Undefined
        if files:
            api_async_files = [convert_async_file_from_domain(file) for file in files]

        return cls(
            ref=ref,
            smartapp_id=bot_id,
            group_chat_id=chat_id,
            data=data,
            opts=opts,
            smartapp_api_version=SMARTAPP_API_VERSION,
            async_files=api_async_files,
        )


class BotXAPISmartAppEventResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]


class SmartAppEventMethod(AuthorizedBotXMethod):
    async def execute(
        self,
        payload: BotXAPISmartAppEventRequestPayload,
    ) -> None:
        path = "/api/v3/botx/smartapps/event"

        # TODO: Remove opts
        # UnverifiedPayloadBaseModel.jsonable_dict remove empty dicts
        json = payload.jsonable_dict()
        json["opts"] = json.get("opts", {})

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=json,
        )

        self._verify_and_extract_api_model(
            BotXAPISmartAppEventResponsePayload,
            response,
        )
