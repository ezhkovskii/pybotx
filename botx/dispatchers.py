import abc
from collections import OrderedDict
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Pattern,
    Tuple,
    Type,
    Union,
)
from uuid import UUID

import aiojobs
from loguru import logger

from .core import BotXException
from .execution import execute_callback_with_exception_catching
from .helpers import create_message
from .models import CommandCallback, CommandHandler, Message, Status, StatusResult


class BaseDispatcher(abc.ABC):
    _handlers: Dict[Pattern, CommandHandler]
    _next_step_handlers: Dict[
        Tuple[str, UUID, UUID, Optional[UUID]], List[CommandCallback]
    ]
    _default_handler: Optional[CommandHandler] = None
    _exceptions_map: Dict[Type[Exception], Callable]

    def __init__(self) -> None:
        self._handlers = OrderedDict()
        self._next_step_handlers = {}
        self._exceptions_map = {}

    def start(self) -> Optional[Awaitable[None]]:
        """Start dispatcher-related things like aiojobs.Scheduler"""

    def shutdown(self) -> Optional[Awaitable[None]]:
        """Stop dispatcher-related things like thread or coroutine joining"""

    @property
    def exception_catchers(self) -> Dict[Type[Exception], Callable]:
        return self._exceptions_map

    @abc.abstractmethod
    def status(self) -> Union[Status, Awaitable[Status]]:
        """Return Status object to be displayed in status menu"""

    @abc.abstractmethod
    def execute_command(self, data: Dict[str, Any]) -> Optional[Awaitable[None]]:
        """Parse request and call status creation or executing handler for handler"""

    def add_handler(self, handler: CommandHandler) -> None:
        logger_ctx = logger.bind(handler=handler.dict())

        if handler.use_as_default_handler:
            logger_ctx.debug("registered default handler")

            self._default_handler = handler
        else:
            logger_ctx.debug(f"registered handler for {handler.command}")

            self._handlers[handler.command] = handler

    def register_next_step_handler(
        self, message: Message, callback: CommandCallback
    ) -> None:
        self._add_next_step_handler(message, callback)

    def register_exception_catcher(
        self, exc: Type[Exception], callback: Callable, force_replace: bool = False
    ) -> None:
        if exc in self._exceptions_map and not force_replace:
            raise BotXException(f"catcher for {exc} was already registered")

        self._exceptions_map[exc] = callback

    def _add_next_step_handler(
        self, message: Message, callback: CommandCallback
    ) -> None:
        key = (message.host, message.bot_id, message.group_chat_id, message.user_huid)
        if key in self._next_step_handlers:
            self._next_step_handlers[key].append(callback)
        else:
            self._next_step_handlers[key] = [callback]

    def _get_callback_for_message(self, message: Message) -> CommandCallback:
        logger_ctx = logger.bind(message=message.dict())

        try:
            callback = self._get_next_step_handler_from_message(message)
            logger_ctx.bind(callback=callback.dict()).debug(
                "found registered next step handler for message"
            )
        except (IndexError, KeyError):
            callback = self._get_command_handler_from_message(message).callback
            logger_ctx.bind(command=message.command.command).debug(
                "found handler for command"
            )

        return callback

    def _get_next_step_handler_from_message(self, message: Message) -> CommandCallback:
        return self._next_step_handlers[
            (message.host, message.bot_id, message.group_chat_id, message.user_huid)
        ].pop()

    def _get_command_handler_from_message(self, message: Message) -> CommandHandler:
        body = message.command.body
        cmd = message.command.command

        handler = None
        for cmd_pattern in self._handlers:
            if cmd_pattern.fullmatch(body):
                handler = self._handlers[cmd_pattern]
                break
            elif cmd_pattern.fullmatch(cmd):
                handler = self._handlers[cmd_pattern]
                break

        if handler:
            return handler

        if self._default_handler:
            return self._default_handler

        raise BotXException(
            "unhandled command with missing handler", data={"handler": message.body}
        )

    def _get_callback_copy_for_message_data(
        self, message_data: Dict[str, Any]
    ) -> CommandCallback:
        message = create_message(message_data)
        logger.bind(message=message.dict()).debug("parsed message successful")

        callback = self._get_callback_for_message(message)
        callback_copy = callback.copy(update={"args": (message,) + callback.args})

        return callback_copy


class AsyncDispatcher(BaseDispatcher):
    _scheduler: aiojobs.Scheduler
    _tasks_limit: int

    def __init__(self, tasks_limit: int) -> None:
        super().__init__()
        self._tasks_limit = tasks_limit

    async def start(self) -> None:
        self._scheduler = await aiojobs.create_scheduler(
            limit=self._tasks_limit, pending_limit=0
        )

    async def shutdown(self) -> None:
        await self._scheduler.close()

    async def status(self) -> Status:
        commands = []
        for _, handler in self._handlers.items():
            menu_command = handler.to_status_command()
            if menu_command:
                commands.append(menu_command)

        return Status(result=StatusResult(commands=commands))

    async def execute_command(self, data: Dict[str, Any]) -> None:
        await self._scheduler.spawn(
            execute_callback_with_exception_catching(
                self.exception_catchers, self._get_callback_copy_for_message_data(data)
            )
        )