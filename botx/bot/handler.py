from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, Awaitable, Callable, List, TypeVar, Union

from botx.models.commands import BotCommand
from botx.models.message.incoming_message import IncomingMessage
from botx.models.status import StatusRecipient
from botx.models.system_events.added_to_chat import AddedToChatEvent
from botx.models.system_events.chat_created import ChatCreatedEvent
from botx.models.system_events.cts_login import CTSLoginEvent
from botx.models.system_events.cts_logout import CTSLogoutEvent
from botx.models.system_events.deleted_from_chat import DeletedFromChatEvent
from botx.models.system_events.internal_bot_notification import (
    InternalBotNotificationEvent,
)
from botx.models.system_events.left_from_chat import LeftFromChatEvent

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440

if TYPE_CHECKING:  # To avoid circular import
    from botx.bot.bot import Bot

TBotCommand = TypeVar("TBotCommand", bound=BotCommand)
HandlerFunc = Callable[[TBotCommand, "Bot"], Awaitable[None]]

IncomingMessageHandlerFunc = HandlerFunc[IncomingMessage]
SystemEventHandlerFunc = Union[
    HandlerFunc[AddedToChatEvent],
    HandlerFunc[ChatCreatedEvent],
    HandlerFunc[DeletedFromChatEvent],
    HandlerFunc[LeftFromChatEvent],
    HandlerFunc[CTSLoginEvent],
    HandlerFunc[CTSLogoutEvent],
    HandlerFunc[InternalBotNotificationEvent],
]

VisibleFunc = Callable[[StatusRecipient, "Bot"], Awaitable[bool]]

Middleware = Callable[
    [IncomingMessage, "Bot", IncomingMessageHandlerFunc],
    Awaitable[None],
]


@dataclass
class BaseIncomingMessageHandler:
    handler_func: IncomingMessageHandlerFunc
    middlewares: List[Middleware]

    async def __call__(self, message: IncomingMessage, bot: "Bot") -> None:
        handler_func = self.handler_func

        for middleware in self.middlewares:
            handler_func = partial(middleware, call_next=handler_func)

        await handler_func(message, bot)

    def add_middlewares(self, middlewares: List[Middleware]) -> None:
        self.middlewares += middlewares


@dataclass
class HiddenCommandHandler(BaseIncomingMessageHandler):
    # Default should be here, see: https://github.com/python/mypy/issues/6113
    visible: Literal[False] = False


@dataclass
class VisibleCommandHandler(BaseIncomingMessageHandler):
    description: str
    visible: Union[Literal[True], VisibleFunc] = True


@dataclass
class DefaultMessageHandler(BaseIncomingMessageHandler):
    """Just for separate type."""


CommandHandler = Union[HiddenCommandHandler, VisibleCommandHandler]
