from typing import AsyncGenerator
from uuid import UUID

import httpx
import pytest

from botx import BotCredentials
from botx.bot.credentials_storage import CredentialsStorage


@pytest.fixture
async def httpx_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient() as client:
        yield client


@pytest.fixture
def host() -> str:
    return "cts.example.com"


@pytest.fixture
def bot_id() -> UUID:
    return UUID("24348246-6791-4ac0-9d86-b948cd6a0e46")


@pytest.fixture
def bot_signature() -> str:
    return "E050AEEA197E0EF0A6E1653E18B7D41C7FDEC0FCFBA44C44FCCD2A88CEABD130"


@pytest.fixture
def bot_credentials(host: str, bot_id: UUID) -> BotCredentials:
    return BotCredentials(
        host=host,
        bot_id=bot_id,
        secret_key="bee001",
    )


@pytest.fixture
def prepared_credentials_storage(
    bot_id: UUID,
    bot_credentials: BotCredentials,
) -> CredentialsStorage:
    credentials_storage = CredentialsStorage([bot_credentials])
    credentials_storage.set_token(bot_id, "token")

    return credentials_storage
