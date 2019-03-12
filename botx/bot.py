import multiprocessing
import io

import requests
from functools import partial
from typing import Optional, Callable, Union, List, Dict, Any, NoReturn
from uuid import UUID

from botx.core.dispatcher import SyncDispatcher
from .base import BotXObject
from .core import CommandHandler
from .types import (
    InputFile,
    ResponseCommand,
    ResponseDocument,
    ResponseNotification,
    ResponseNotificationResult,
    ResponseCommandResult,
    SyncID,
    BubbleElement,
    KeyboardElement,
    ResponseRecipientsEnum,
    Status,
)

_BOTX_AUTH_URL = "https://{}/api/v2/botx/bots/{}/token"
_BOTX_COMMAND_CALLBACK = "https://{}/api/v2/botx/command/callback"
_BOTX_NOTIFICATION_CALLBACK = "https://{}/api/v2/botx/notification/callback"
_BOTX_FILE_CALLBACK = "https://{}/api/v1/botx/file/callback"


class Bot(BotXObject):
    bot_id: UUID
    bot_host: str
    workers: Optional[int] = multiprocessing.cpu_count()
    _token: str

    def __init__(self, bot_id: UUID, bot_host: str):
        super().__init__(bot_id=bot_id, bot_host=bot_host)

        self.url_command = _BOTX_COMMAND_CALLBACK.format(self.bot_host)
        self.url_notification = _BOTX_NOTIFICATION_CALLBACK.format(self.bot_host)
        self.url_file = _BOTX_FILE_CALLBACK.format(self.bot_host)

        self._dispatcher = SyncDispatcher(bot=self, workers=self.workers)

    def stop_bot(self) -> NoReturn:
        self._dispatcher.shutdown()

    def add_handler(self, handler: CommandHandler) -> NoReturn:
        self._dispatcher.add_handler(handler)

    def command(
        self,
        func: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        body: Optional[str] = None,
    ) -> Optional[Callable]:
        if func:
            name = (
                name or func.__name__.lower().rsplit("command", 1)[0].rsplit("_", 1)[0]
            )
            body = body or f"/{name}"
            description = description or f"{name} command"

            self.add_handler(
                CommandHandler(
                    command=body,
                    func=func,
                    name=name.capitalize(),
                    description=description,
                )
            )
        else:
            return partial(self.command, name=name, description=description, body=body)

    def parse_status(self, data: Dict[str, Any]) -> Status:
        return self._dispatcher.parse_request(data, request_type="status")

    def parse_command(self, data: Dict[str, Any]) -> bool:
        return self._dispatcher.parse_request(data, request_type="command")

    def send_message(
        self,
        chat_id: Union[SyncID, UUID, List[UUID]],
        text: str,
        recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all,
        bubble: Optional[List[List[BubbleElement]]] = None,
        keyboard: Optional[List[List[KeyboardElement]]] = None,
    ) -> NoReturn:
        if not bubble:
            bubble = []
        if not keyboard:
            keyboard = []

        if isinstance(chat_id, SyncID):
            self._send_command_result(chat_id, text, recipients, bubble, keyboard)
        elif isinstance(chat_id, UUID) or isinstance(chat_id, list):
            group_chat_ids = []
            if isinstance(chat_id, UUID):
                group_chat_ids.append(chat_id)
            elif isinstance(chat_id, list):
                group_chat_ids = chat_id
            self._send_notification_result(
                group_chat_ids, text, recipients, bubble, keyboard
            )

    def _send_command_result(
        self,
        chat_id: SyncID,
        text: str,
        recipients: Union[List[UUID], str],
        bubble: List[List[BubbleElement]],
        keyboard: List[List[KeyboardElement]],
    ):
        response_result = ResponseCommandResult(
            body=text, bubble=bubble, keyboard=keyboard
        )

        response = ResponseCommand(
            bot_id=self.bot_id,
            sync_id=str(chat_id),
            command_result=response_result,
            recipients=recipients,
        ).dict()
        requests.post(self.url_command, data=response)

    def _send_notification_result(
        self,
        group_chat_ids: List[UUID],
        text: str,
        recipients: Union[List[UUID], str],
        bubble: List[List[BubbleElement]],
        keyboard: List[List[KeyboardElement]],
    ):
        response_result = ResponseNotificationResult(
            body=text, bubble=bubble, keyboard=keyboard
        )
        response = ResponseNotification(
            bot_id=self.bot_id,
            notification=response_result,
            group_chat_ids=group_chat_ids,
            recipients=recipients,
        ).dict()
        requests.post(self.url_notification, data=response)

    def send_document(self, chat_id: Union[SyncID, UUID], document: bytes):
        files = {"file": document}
        response = ResponseDocument(bot_id=self.bot_id, sync_id=chat_id)

        requests.post(self.url_file, files=files, data=response.dict())
