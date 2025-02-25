# SPDX-License-Identifier: Apache-2.0

import asyncio

from beeai_framework.agents.bee.agent import BeeAgent
from beeai_framework.agents.types import BeeInput, BeeRunOutput
from beeai_framework.backend.chat import ChatModel
from beeai_framework.emitter import Emitter, EventMeta
from beeai_framework.memory.unconstrained_memory import UnconstrainedMemory
from beeai_framework.tools.search import DuckDuckGoSearchTool
from beeai_framework.tools.weather.openmeteo import OpenMeteoTool
from examples.helpers.io import prompt_input


async def main() -> None:
    chat_model: ChatModel = await ChatModel.from_name("ollama:granite3.1-dense:8b")

    agent = BeeAgent(
        BeeInput(
            llm=chat_model, tools=[OpenMeteoTool(), DuckDuckGoSearchTool(max_results=3)], memory=UnconstrainedMemory()
        )
    )

    prompt = prompt_input(default="How is the weather in White Plains?")

    async def update_callback(data: dict, event: EventMeta) -> None:
        print(f"Agent({data['update']['key']}) 🤖 : ", data["update"]["parsedValue"])

    async def observe(emitter: Emitter) -> None:
        emitter.on("update", update_callback)

    output: BeeRunOutput = await agent.run(
        {"prompt": prompt},
        {"execution": {"total_max_retries": 2, "max_retries_per_step": 3, "max_iterations": 8}},
    ).observe(observe)

    print("Agent 🤖 : ", output.result.text)


if __name__ == "__main__":
    asyncio.run(main())
