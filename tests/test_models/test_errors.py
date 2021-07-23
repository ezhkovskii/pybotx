import pytest
from pydantic import ValidationError

from botx import BotDisabledErrorData, BotDisabledResponse


def test_error_for_missing_status_message_field():
    with pytest.raises(ValidationError):
        BotDisabledResponse(error_data={})


def test_doing_nothing_when_passed_error_data_model():
    response = BotDisabledResponse(
        error_data=BotDisabledErrorData(status_message="test"),
    )
    assert response.error_data.status_message == "test"
