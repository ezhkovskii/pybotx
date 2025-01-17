import asyncio
from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
    Bot,
    BotAccountWithSecret,
    BubbleMarkup,
    Button,
    HandlerCollector,
    KeyboardMarkup,
    lifespan_wrapper,
)
from pybotx.models.message.markup import ButtonTextAlign

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__markup__defaults_filled(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "notification": {
                "status": "ok",
                "body": "Hi!",
                "bubble": [
                    [
                        {
                            "command": "/bubble-button",
                            "data": {},
                            "label": "Bubble button",
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                ],
                "keyboard": [
                    [
                        {
                            "command": "/keyboard-button",
                            "data": {},
                            "label": "Keyboard button",
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                ],
            },
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command="/bubble-button",
        label="Bubble button",
    )

    keyboard = KeyboardMarkup()
    keyboard.add_button(
        command="/keyboard-button",
        label="Keyboard button",
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.send_message(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                bubbles=bubbles,
                keyboard=keyboard,
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        await bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
        )

    # - Assert -
    assert (await task) == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called


async def test__markup__correctly_built(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "notification": {
                "status": "ok",
                "body": "Hi!",
                "bubble": [
                    [
                        {
                            "command": "/bubble-button-1",
                            "data": {},
                            "label": "Bubble button 1",
                            "opts": {"silent": True, "align": "center"},
                        },
                        {
                            "command": "/bubble-button-2",
                            "data": {},
                            "label": "Bubble button 2",
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                    [
                        {
                            "command": "/bubble-button-3",
                            "data": {},
                            "label": "Bubble button 3",
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                    [
                        {
                            "command": "/bubble-button-4",
                            "data": {},
                            "label": "Bubble button 4",
                            "opts": {"silent": True, "align": "center"},
                        },
                        {
                            "command": "/bubble-button-5",
                            "data": {},
                            "label": "Bubble button 5",
                            "opts": {"silent": True, "align": "center"},
                        },
                    ],
                ],
            },
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    bubbles = BubbleMarkup()

    bubbles.add_button(
        command="/bubble-button-1",
        label="Bubble button 1",
        new_row=False,
    )
    bubbles.add_button(
        command="/bubble-button-2",
        label="Bubble button 2",
        new_row=False,
    )
    bubbles.add_button(
        command="/bubble-button-3",
        label="Bubble button 3",
    )

    button_4 = Button(
        command="/bubble-button-4",
        label="Bubble button 4",
    )
    button_5 = Button(
        command="/bubble-button-5",
        label="Bubble button 5",
    )
    bubbles.add_row([button_4, button_5])

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.send_message(
                body="Hi!",
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                bubbles=bubbles,
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        await bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
        )

    # - Assert -
    assert (await task) == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called


async def test__markup__color_and_align(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    endpoint = respx_mock.post(
        f"https://{host}/api/v4/botx/notifications/direct",
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
        json={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "notification": {
                "body": "Buttons styles:",
                "bubble": [
                    [
                        {
                            "command": "/button",
                            "data": {},
                            "label": "Green font, left align",
                            "opts": {
                                "font_color": "#25B43D",
                                "align": "left",
                                "silent": True,
                            },
                        },
                    ],
                    [
                        {
                            "command": "/button",
                            "data": {},
                            "label": "Green background, center align",
                            "opts": {
                                "background_color": "#25B43D",
                                "align": "center",
                                "silent": True,
                            },
                        },
                    ],
                    [
                        {
                            "command": "/button",
                            "data": {},
                            "label": "Red font, green background, right align",
                            "opts": {
                                "font_color": "#ED4747",
                                "background_color": "#25B43D",
                                "align": "right",
                                "silent": True,
                            },
                        },
                    ],
                ],
                "keyboard": [
                    [
                        {
                            "command": "/keyboard",
                            "data": {},
                            "label": "Green background, left align",
                            "opts": {
                                "background_color": "#25B43D",
                                "align": "left",
                                "silent": True,
                            },
                        },
                    ],
                ],
                "status": "ok",
            },
        },
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.ACCEPTED,
            json={
                "status": "ok",
                "result": {"sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"},
            },
        ),
    )

    bubbles = BubbleMarkup()

    bubbles.add_button(
        command="/button",
        label="Green font, left align",
        text_color="#25B43D",
        align=ButtonTextAlign.LEFT,
    )
    bubbles.add_button(
        command="/button",
        label="Green background, center align",
        background_color="#25B43D",
        align=ButtonTextAlign.CENTER,
    )
    bubbles.add_button(
        command="/button",
        label="Red font, green background, right align",
        text_color="#ED4747",
        background_color="#25B43D",
        align=ButtonTextAlign.RIGHT,
    )

    keyboard = KeyboardMarkup()
    keyboard.add_button(
        command="/keyboard",
        label="Green background, left align",
        background_color="#25B43D",
        align=ButtonTextAlign.LEFT,
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task = asyncio.create_task(
            bot.send_message(
                body="Buttons styles:",
                bot_id=bot_id,
                chat_id=UUID("054af49e-5e18-4dca-ad73-4f96b6de63fa"),
                bubbles=bubbles,
                keyboard=keyboard,
            ),
        )

        await asyncio.sleep(0)  # Return control to event loop

        await bot.set_raw_botx_method_result(
            {
                "status": "ok",
                "sync_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
                "result": {},
            },
        )

    # - Assert -
    assert (await task) == UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    assert endpoint.called


def test__markup__comparison() -> None:
    # - Arrange -
    button = Button("/test", "test")

    # - Assert -
    assert BubbleMarkup([[button]]) == BubbleMarkup([[button]])
