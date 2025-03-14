# Copyright 2025 IBM Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from beeai_framework.adapters.ollama.backend.chat import OllamaChatModel
from beeai_framework.agents.react import ReActAgent
from beeai_framework.agents.types import AgentMeta
from beeai_framework.backend.message import UserMessage
from beeai_framework.memory import TokenMemory, UnconstrainedMemory
from beeai_framework.workflows.agent import AgentFactoryInput, AgentWorkflow

"""
E2E Tests
"""


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multi_agents_workflow_basic() -> None:
    chat_model = OllamaChatModel()

    workflow: AgentWorkflow = AgentWorkflow()
    workflow.add_agent(AgentFactoryInput(name="Translator assistant", tools=[], llm=chat_model))

    memory = UnconstrainedMemory()
    await memory.add(UserMessage(content="Translate 'Hello' to German."))
    response = await workflow.run(memory.messages)
    print(response.state)
    assert "hallo" in response.state.final_answer.lower()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multi_agents_workflow_creation() -> None:
    chat_model = OllamaChatModel()

    workflow: AgentWorkflow = AgentWorkflow()
    workflow.add_agent(ReActAgent(llm=chat_model, tools=[], memory=TokenMemory(chat_model)))
    workflow.add_agent(lambda mem: ReActAgent(llm=chat_model, tools=[], memory=mem))

    assert len(workflow.workflow.step_names) == 2

    memory = UnconstrainedMemory()
    await memory.add(UserMessage(content="Translate 'Good morning' to Italian."))
    response = await workflow.run(memory.messages)
    assert "buongiorno" in response.state.final_answer.lower()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multi_agents_workflow_creation_variations() -> None:
    chat_model = OllamaChatModel()

    workflow: AgentWorkflow = AgentWorkflow()

    # AgentFactoryInput
    workflow.add_agent(name="AgentFactoryInput_1", tools=[], llm=chat_model)
    workflow.add_agent(agent=AgentFactoryInput(name="AgentFactoryInput_2", tools=[], llm=chat_model))

    # ReActAgent
    workflow.add_agent(
        agent=ReActAgent(
            llm=chat_model,
            tools=[],
            memory=TokenMemory(chat_model),
            meta=AgentMeta(name="ReActAgent_1", tools=[], description="ReActAgent defined using agent keyword"),
        )
    )

    assert len(workflow.workflow.step_names) == 3
    assert set(workflow.workflow.steps.keys()) == {
        "AgentFactoryInput_1",
        "AgentFactoryInput_2",
        "ReActAgent_1",
    }

    memory = UnconstrainedMemory()
    await memory.add(UserMessage(content="Translate 'Good morning' to Portuguese."))
    response = await workflow.run(memory.messages)
    assert "bom dia" in response.state.final_answer.lower()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multi_agents_workflow_agent_delete() -> None:
    chat_model = OllamaChatModel()

    workflow: AgentWorkflow = AgentWorkflow()
    workflow.add_agent(ReActAgent(llm=chat_model, tools=[], memory=UnconstrainedMemory()))
    workflow.del_agent("ReAct")
    workflow.add_agent(ReActAgent(llm=chat_model, tools=[], memory=UnconstrainedMemory()))

    assert len(workflow.workflow.step_names) == 1
