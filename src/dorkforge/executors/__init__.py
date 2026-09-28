"""Live-execution plug-in interface (v2). No executors are implemented in v1."""

from dorkforge.executors.base import Executor, ExecutorResult

__all__ = ["Executor", "ExecutorResult"]
