from abc import ABC, abstractmethod
from typing import List, Optional

from g3py.decl import Metric, MetricDict, MetricChangeDict

from switchmap import inputComparators, outputMap, outputValue


class ArduinoBase(ABC):
    def __init__(self):
        self._in_state = MetricChangeDict(comparators=inputComparators)
        self._out_state = MetricChangeDict()

    @abstractmethod
    def _poll(self) -> MetricDict:
        ...

    def get_state(self) -> MetricChangeDict:
        self._in_state.update(self._poll())
        return self._in_state

    def get_state_changes(self) -> MetricDict:
        t = self._in_state.latest()
        self.get_state()
        return self._in_state.changed_since(t)

    def output_names(self) -> List[Metric]:
        return [k for k in outputMap if k]

    def set_test(self, on: bool) -> None:
        self.set_state({k: on for k in self.output_names()})

    def _maybe_output(self, state: MetricDict) -> Optional[int]:
        state = {k: v for (k, v) in state.items() if k in self.output_names()}
        if not state:
            return None
        changes = self._out_state.update_changed(state)
        if not changes:
            return None
        return outputValue(self._out_state)

    @abstractmethod
    def set_state(self, state: MetricDict) -> None:
        ...
