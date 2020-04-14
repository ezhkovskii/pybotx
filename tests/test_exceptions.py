import pytest

from botx import (
    Bot,
    BotXAPIError,
    IncomingMessage,
    Message,
    ServerUnknownError,
    testing,
)
from botx.exceptions import NoMatchFound


@pytest.mark.asyncio
async def test_response_info_in_BotXAPIError(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    message = Message.from_dict(incoming_message.dict(), bot)
    with testing.TestClient(bot, generate_error_api=True):
        with pytest.raises(BotXAPIError) as err_info:
            await bot.send_message("text", message.credentials)
        error = err_info.value
        assert error.response_content == {"result": "API error"}


@pytest.mark.asyncio
async def test_host_in_ServerUnknownError(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    incoming_message.user.host = "wrong.com"
    with pytest.raises(ServerUnknownError) as err_info:
        await bot.execute_command(incoming_message.dict())

    error = err_info.value
    assert error.host == "wrong.com"


@pytest.mark.asyncio
async def test_search_param_in_NoMatchFound_error(
    bot: Bot, incoming_message: IncomingMessage
) -> None:
    incoming_message.command.body = "/wrong-command"
    message = Message.from_dict(incoming_message.dict(), bot)

    with pytest.raises(NoMatchFound) as err_info:
        bot.collector.default_message_handler = None
        await bot.collector.handle_message(message)

    error = err_info.value
    assert error.search_param == "/wrong-command"