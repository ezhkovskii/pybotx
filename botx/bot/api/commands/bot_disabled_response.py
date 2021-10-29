from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


@dataclass
class BotAPIBotDisabledErrorData:
    status_message: str


@dataclass
class BotAPIBotDisabledResponse:
    """Disabled bot response model.

    Only `.error_data.status_message` attribute will be displayed to
    user. Other attributes will be visible only in BotX logs.
    """

    error_data: BotAPIBotDisabledErrorData
    errors: List[str] = field(default_factory=list)
    reason: Literal["bot_disabled"] = "bot_disabled"


def build_bot_disabled_response(status_message: str) -> Dict[str, Any]:
    """Build bot disabled response for BotX.

    It should be send if the bot can't process the command.

    If you would like to build complex response, see
    [BotAPIBotDisabledResponse]
    [botx.bot.api.commands.bot_disabled_response.BotAPIBotDisabledResponse].

    Arguments:
        status_message: Status message.

    Returns:
        built bot disabled response.
    """

    response = BotAPIBotDisabledResponse(
        error_data=BotAPIBotDisabledErrorData(status_message=status_message),
    )

    return asdict(response)
