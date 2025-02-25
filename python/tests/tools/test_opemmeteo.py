# SPDX-License-Identifier: Apache-2.0

import pytest

from beeai_framework.tools import ToolInputValidationError
from beeai_framework.tools.tool import StringToolOutput
from beeai_framework.tools.weather.openmeteo import OpenMeteoTool, OpenMeteoToolInput


@pytest.fixture
def tool() -> OpenMeteoTool:
    return OpenMeteoTool()


@pytest.mark.e2e
def test_call_model(tool: OpenMeteoTool) -> None:
    tool.run(
        input=OpenMeteoToolInput(
            location_name="Cambridge",
            country="US",
            temperature_unit="fahrenheit",
        )
    )


@pytest.mark.e2e
def test_call_dict(tool: OpenMeteoTool) -> None:
    tool.run(input={"location_name": "White Plains"})


@pytest.mark.e2e
def test_call_invalid_missing_field(tool: OpenMeteoTool) -> None:
    with pytest.raises(ToolInputValidationError):
        tool.run(input={})


@pytest.mark.e2e
def test_call_invalid_bad_type(tool: OpenMeteoTool) -> None:
    with pytest.raises(ToolInputValidationError):
        tool.run(input={"location_name": 1})


@pytest.mark.e2e
def test_output(tool: OpenMeteoTool) -> None:
    result = tool.run(input={"location_name": "White Plains"})
    assert type(result) is StringToolOutput
    assert "current" in result.get_text_content()


@pytest.mark.e2e
def test_bad_start_date_format(tool: OpenMeteoTool) -> None:
    with pytest.raises(ToolInputValidationError):
        tool.run(input=OpenMeteoToolInput(location_name="White Plains", start_date="2025:01:01", end_date="2025:01:02"))


@pytest.mark.e2e
def test_bad_end_date_format(tool: OpenMeteoTool) -> None:
    with pytest.raises(ToolInputValidationError):
        tool.run(input=OpenMeteoToolInput(location_name="White Plains", start_date="2025-01-01", end_date="2025:01:02"))


@pytest.mark.e2e
def test_bad_dates(tool: OpenMeteoTool) -> None:
    with pytest.raises(ToolInputValidationError):
        tool.run(input=OpenMeteoToolInput(location_name="White Plains", start_date="2025-02-02", end_date="2025-02-01"))
