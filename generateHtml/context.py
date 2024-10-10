from __future__ import annotations
from contextvars import ContextVar
from abc import abstractmethod, ABC


class ContextStack(ABC):
    _context_var: ContextVar[list[list[ContextStack]] | None] = ContextVar(
        "storage", default=None
    )

    def __init__(self):
        self._add_to_context(self)

    @property
    def _context_elements(self) -> list[list[ContextStack]] | None:
        context_elements = self._context_var.get()
        if context_elements is None:
            context_elements = []
            self._context_var.set(context_elements)
        return context_elements

    # Context manipulation methods
    def _add_to_context(self, element: ContextStack) -> None:
        if self._context_elements:
            self._context_elements[-1].append(element)

    def _remove_from_context(self, element: ContextStack) -> None:
        if self._context_elements and element in self._context_elements[-1]:
            self._context_elements[-1].remove(element)
        self._clear_context_elements()

    def _clear_context_elements(self) -> None:
        if not self._context_elements:
            self._context_var.set(None)

    # Context manager methods
    def __enter__(self):
        self._context_elements.append([])
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for child in self._context_elements.pop():
            self.add(child)
        self._clear_context_elements()

    @abstractmethod
    def add(self, *args):
        """Method for adding arguments into context stack"""
