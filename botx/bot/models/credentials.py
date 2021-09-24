from dataclasses import dataclass
from uuid import UUID


@dataclass
class BotCredentials:
    host: str
    bot_id: UUID
    secret_key: str
