import pytest

from botx import BotXException, CommandHandler, RequestTypeEnum, Status, StatusResult
from botx.bot.dispatcher.syncdispatcher import SyncDispatcher


def test_sync_dispatcher_attributes():
    d = SyncDispatcher(workers=1)
    assert d._pool is not None
    assert d._pool._max_workers == 1
    d.shutdown()


def test_sync_dispatcher_wrong_request_parsing():
    d = SyncDispatcher(workers=1)
    with pytest.raises(BotXException):
        d.parse_request({}, request_type="wrong type")
    d.shutdown()


def test_sync_dispatcher_command_request_parsing(command_with_text_and_file):
    d = SyncDispatcher(workers=1)
    r = d.parse_request(command_with_text_and_file, RequestTypeEnum.command)
    assert not r
    d.shutdown()


def test_sync_dispatcher_default_handler_processing(command_with_text_and_file):
    d = SyncDispatcher(workers=1)
    result_array = []

    def handler_function(message):
        result_array.append("default")

    d.add_handler(
        CommandHandler(
            command="/cmd",
            name="handler",
            description="description",
            func=handler_function,
            use_as_default_handler=True,
        )
    )

    d.parse_request(command_with_text_and_file, request_type="command")

    d.shutdown()

    assert len(result_array) == 1
    assert result_array[0] == "default"


def test_sync_dispatcher_message_creation(command_with_text_and_file):
    d = SyncDispatcher(workers=3)
    result_array = []

    def handler_function(message):
        result_array.append(message.body)

    d.add_handler(
        CommandHandler(
            command="/cmd",
            name="handler",
            description="description",
            func=handler_function,
        )
    )

    for _ in range(3):
        d.parse_request(command_with_text_and_file, request_type="command")

    d.shutdown()

    assert len(result_array) == 3
    for r in result_array:
        assert r == "/cmd arg"


def test_sync_dispatcher_status_creation(custom_handler):
    d = SyncDispatcher(workers=4)
    d.add_handler(custom_handler)
    assert d.parse_request({}, request_type="status") == Status(
        result=StatusResult(commands=[custom_handler.to_status_command()])
    )


def test_sync_dispatcher_not_accepting_coroutine_as_handler():
    d = SyncDispatcher(workers=4)

    async def f(m):
        pass

    with pytest.raises(BotXException):
        d.add_handler(CommandHandler(name="a", command="a", description="a", func=f))
