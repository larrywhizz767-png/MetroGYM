from __future__ import annotations

import json
import os
from typing import Any

from metrogym.primitives.signal.llm_signal_queue_handler import BaseLLMProvider, SignalQueuePlan


class OpenAIELLProvider(BaseLLMProvider):
    def __init__(self):
        self._planners: dict[tuple[str, str], Any] = {}

    def select_train(
        self,
        *,
        model: str,
        decision_prompt: str,
        payload: dict[str, object],
    ) -> SignalQueuePlan:
        response = self._load_planner(model, decision_prompt)(json.dumps(payload, indent=2))
        parsed = getattr(response, "parsed", None)
        if parsed is None:
            raise ValueError("ELL did not return structured parsed output.")
        return SignalQueuePlan(
            selected_train_id=str(parsed.selected_train_id),
            reason=str(parsed.reason),
            queue_order=tuple(payload.get("queue_order", ())),
        )

    def _load_planner(self, model: str, decision_prompt: str) -> Any:
        key = (model, decision_prompt)
        if key in self._planners:
            return self._planners[key]
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required for OpenAIELLProvider.")
        try:
            import ell
            from pydantic import BaseModel
        except ImportError as exc:
            raise RuntimeError("ELL is not installed. Install with `uv sync --extra llm`.") from exc

        class QueueChoice(BaseModel):
            selected_train_id: str
            reason: str

        @ell.complex(model=model, response_format=QueueChoice)
        def choose_train(prompt: str):
            """placeholder"""
            return prompt

        choose_train.__doc__ = (
            f"{decision_prompt}\n\n" if decision_prompt else ""
        ) + (
            "Return structured output with fields `selected_train_id` and `reason`. "
            "`selected_train_id` must exactly match one candidate train_id from the prompt."
        )
        self._planners[key] = choose_train
        return choose_train
