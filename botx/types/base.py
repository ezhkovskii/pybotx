import json
from uuid import UUID

from botx.core import BotXObject
from pydantic import BaseConfig


class _UUIDJSONEncoder(json.JSONEncoder):
    def default(self, o):  # pylint: disable=method-hidden
        if isinstance(o, UUID):
            return str(o)

        return super().default(o)


class BotXType(BotXObject):
    class Config(BaseConfig):  # pylint: disable=too-few-public-methods
        allow_population_by_alias = True

    def json(
        self, *, by_alias: bool = True, **kwargs
    ):  # pylint: disable=arguments-differ
        return super().json(by_alias=by_alias, **kwargs)

    def dict(
        self, *, by_alias: bool = True, **kwargs
    ):  # pylint: disable=arguments-differ
        return json.loads(
            json.dumps(super().dict(by_alias=by_alias, **kwargs), cls=_UUIDJSONEncoder)
        )
