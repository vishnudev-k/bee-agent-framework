# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod

from beeai_framework.agents.types import AgentMeta, BeeRunInput, BeeRunOptions, BeeRunOutput
from beeai_framework.context import Run, RunContext, RunContextInput, RunInstance
from beeai_framework.emitter import Emitter
from beeai_framework.memory import BaseMemory
from beeai_framework.utils.models import ModelLike, to_model, to_model_optional


class BaseAgent(ABC):
    is_running: bool = False
    emitter: Emitter = None

    def run(self, run_input: ModelLike[BeeRunInput], options: ModelLike[BeeRunOptions] | None = None) -> Run:
        run_input = to_model(BeeRunInput, run_input)
        options = to_model_optional(BeeRunOptions, options)

        if self.is_running:
            raise RuntimeError("Agent is already running!")

        try:
            return RunContext.enter(
                RunInstance(emitter=self.emitter),
                RunContextInput(signal=options.signal if options else None, params=(run_input, options)),
                lambda context: self._run(run_input, options, context),
            )
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise e
            else:
                raise RuntimeError("Error has occurred!") from e
        finally:
            self.is_running = False

    @abstractmethod
    async def _run(self, run_input: BeeRunInput, options: BeeRunOptions | None, context: RunContext) -> BeeRunOutput:
        pass

    def destroy(self) -> None:
        self.emitter.destroy()

    @property
    @abstractmethod
    def memory(self) -> BaseMemory:
        pass

    @memory.setter
    @abstractmethod
    def memory(self, memory: BaseMemory) -> None:
        pass

    @property
    def meta(self) -> AgentMeta:
        return AgentMeta(
            name=self.__class__.__name__,
            description="",
            tools=[],
        )
