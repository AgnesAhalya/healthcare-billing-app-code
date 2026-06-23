
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class ActionResult:
    message: str
    payload: Any = None
    redirect_to: str | None = None


class ActionService(ABC):
    @abstractmethod
    def execute(self, form: Mapping[str, Any], files: Mapping[str, Any], actor: Any) -> ActionResult:
        raise NotImplementedError


class Repository(ABC):
    pass
