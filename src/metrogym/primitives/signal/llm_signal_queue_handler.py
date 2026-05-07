from __future__ import annotations

"""Public LLM-backed signal queue helpers.

These helpers expose an optional solver family for junctions where multiple
trains approach one protected signal and a language model chooses the next train
to release.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass

from beartype import beartype

from metrogym.primitives.signal.extras.control_rule import ControlRuleLike
from metrogym.primitives.signal.signal import Signal
from metrogym.solvers import SignalAgent, SignalObservation, signal


@beartype
@dataclass(frozen=True)
class SignalQueueCandidate:
    """Describe one train candidate waiting for an LLM queue decision.

    Args:
        train_id (str):
            Candidate train identifier.
        line_name (str):
            Candidate line name.
        distance_to_signal (float):
            Distance from the train to the signal.
        stopped (bool):
            Whether the train is currently stopped.
        wait_ticks (int):
            Number of ticks the train has been waiting.
        speed (float):
            Current train speed.
    """

    train_id: str
    line_name: str
    distance_to_signal: float
    stopped: bool
    wait_ticks: int
    speed: float


@beartype
@dataclass(frozen=True)
class SignalQueuePlan:
    """Represent the structured result returned by an LLM provider.

    Args:
        selected_train_id (str):
            Train identifier chosen to receive the next grant.
        reason (str):
            Human-readable explanation for the choice.
        queue_order (tuple[str, ...], default=()):
            Observed queue order used to make the decision.
    """

    selected_train_id: str
    reason: str
    queue_order: tuple[str, ...] = ()


class BaseLLMProvider(ABC):
    """Abstract provider interface for LLM queue planning."""

    @abstractmethod
    def select_train(
        self,
        *,
        model: str,
        decision_prompt: str,
        payload: dict[str, object],
    ) -> SignalQueuePlan:
        """Choose the next train to grant through a protected signal.

        Args:
            model (str):
                Provider-specific model identifier.
            decision_prompt (str):
                Optional user-supplied planning prompt.
            payload (dict[str, object]):
                Structured queue state sent to the provider.

        Returns:
            SignalQueuePlan:
                Structured queueing decision.
        """
        raise NotImplementedError


class BaseLLMQueueSignalAgent(SignalAgent):
    """Signal agent that delegates queue selection to an LLM provider.

    Args:
        provider (BaseLLMProvider):
            Provider implementation used to select trains.
        model (str):
            Provider-specific model identifier.
        decision_prompt (str, default=""):
            Optional extra prompt context.
        include_signal_state (bool, default=True):
            Include current signal state in the provider payload.
        include_queue_candidates (bool, default=True):
            Include structured candidate rows in the provider payload.
        include_world_state (bool, default=False):
            Include a broader world snapshot in the provider payload.
        approach_distance (float, default=90.0):
            Maximum distance for a train to join the queue.
        release_distance (float, default=110.0):
            Distance after which the granted train releases the lock.
        red_hold_ticks (int, default=3):
            Number of all-red ticks before asking the provider.
    """

    def __init__(
        self,
        provider: BaseLLMProvider,
        *,
        model: str,
        decision_prompt: str = "",
        include_signal_state: bool = True,
        include_queue_candidates: bool = True,
        include_world_state: bool = False,
        approach_distance: float = 90.0,
        release_distance: float = 110.0,
        red_hold_ticks: int = 3,
    ):
        self.provider = provider
        self.model = model
        self.decision_prompt = decision_prompt
        self.include_signal_state = include_signal_state
        self.include_queue_candidates = include_queue_candidates
        self.include_world_state = include_world_state
        self.approach_distance = approach_distance
        self.release_distance = release_distance
        self.red_hold_ticks = red_hold_ticks
        self.active_train_id: str | None = None
        self.phase = "open"
        self.red_since = 0

    def reset(self) -> None:
        """Reset internal queue state."""
        self.active_train_id = None
        self.phase = "open"
        self.red_since = 0

    def act(self, observation: SignalObservation):
        """Select the next signal action from queue state.

        Args:
            observation (SignalObservation):
                Signal-centric observation.

        Returns:
            object:
                Signal decision generated by the LLM queueing workflow.
        """
        approaching = observation.queue.ordered(approach_distance=self.approach_distance, moving_only=True)
        if self.active_train_id is not None and self.active_train_id in observation.trains:
            active_train = observation.trains[self.active_train_id]
            if observation.queue.distance_for(active_train) > self.release_distance:
                self.active_train_id = None
                self.phase = "open"
        if self.phase == "open" and len(approaching) >= 2:
            self.phase = "all_red"
            self.red_since = observation.tick
            return signal.lock_all(reason="llm queue planner collecting candidates")
        if self.phase == "all_red":
            if observation.tick - self.red_since < self.red_hold_ticks:
                return signal.lock_all(reason="llm queue planner retaining all trains")
            candidates = [
                SignalQueueCandidate(
                    train_id=next_train.id,
                    line_name=next_train.line_name,
                    distance_to_signal=observation.queue.distance_for(next_train),
                    stopped=next_train.stopped,
                    wait_ticks=next_train.wait_ticks,
                    speed=next_train.speed,
                )
                for next_train in approaching
            ]
            plan = self.provider.select_train(
                model=self.model,
                decision_prompt=self.decision_prompt,
                payload=self._prompt_payload(observation, candidates),
            )
            valid_ids = {candidate.train_id for candidate in candidates}
            if plan.selected_train_id not in valid_ids:
                raise ValueError(f"LLM returned invalid train id: {plan.selected_train_id!r}")
            self.active_train_id = plan.selected_train_id
            self.phase = "grant"
            return signal.grant(train_id=self.active_train_id, reason=plan.reason)
        if self.phase == "grant" and self.active_train_id is not None:
            return signal.grant(train_id=self.active_train_id, reason="llm queue grant remains active")
        return signal.grant(reason="junction open")

    def _prompt_payload(self, observation: SignalObservation, candidates: list[SignalQueueCandidate]) -> dict[str, object]:
        payload: dict[str, object] = {
            "signal_id": observation.self.id,
            "queue_order": [candidate.train_id for candidate in candidates],
        }
        if self.include_signal_state:
            payload["signal_state"] = {
                "tick": observation.tick,
                "green": observation.self.green,
                "granted_train_id": observation.self.granted_train_id,
                "granted_line": observation.self.granted_line,
            }
        if self.include_queue_candidates:
            payload["queue_candidates"] = [candidate.__dict__ for candidate in candidates]
        if self.include_world_state:
            payload["world_state"] = {
                "all_trains": {
                    train_id: {
                        "line_name": next_train.line_name,
                        "stopped": next_train.stopped,
                        "wait_ticks": next_train.wait_ticks,
                        "speed": next_train.speed,
                        "target_speed": next_train.target_speed,
                        "distance_to_signal": observation.queue.distance_for(next_train),
                    }
                    for train_id, next_train in observation.trains.items()
                },
                "collisions": [
                    {
                        "train_id": event.train_id,
                        "peer_id": event.peer_id,
                        "position": event.position.pygame(),
                    }
                    for event in observation.collision_events
                ],
            }
        return payload


@beartype
class LLMSignalQueueHandler(Signal):
    """Signal primitive wired to an LLM-backed queue-planning agent.

    Args:
        id (str):
            Unique signal identifier.
        position (object):
            Signal position accepted by the base :class:`Signal` primitive.
        controls (ControlRuleLike | Iterable[ControlRuleLike] | None, default=None):
            Protected segments controlled by the signal.
        label (str | None, default=None):
            Optional signal label.
        provider (BaseLLMProvider | None, default=None):
            Explicit provider implementation. If omitted, use ``provider_name``.
        provider_name (str, default="openai"):
            Named provider implementation to resolve.
        model (str, default="gpt-4o-mini"):
            Provider-specific model identifier.
        decision_prompt (str, default=""):
            Optional extra planning prompt.
        include_signal_state (bool, default=True):
            Include current signal state in the LLM payload.
        include_queue_candidates (bool, default=True):
            Include structured candidate rows in the LLM payload.
        include_world_state (bool, default=False):
            Include a broader world snapshot in the LLM payload.
        approach_distance (float, default=90.0):
            Maximum distance for a train to join the queue.
        release_distance (float, default=110.0):
            Distance after which the granted train releases the lock.
        red_hold_ticks (int, default=3):
            Number of all-red ticks before asking the provider.
        initial_green (bool, default=True):
            Initial light state.
        period_ticks (int, default=5):
            Timer period used by the underlying runtime light.
    """

    def __init__(
        self,
        id: str,
        position: object,
        *,
        controls: ControlRuleLike | Iterable[ControlRuleLike] | None = None,
        label: str | None = None,
        provider: BaseLLMProvider | None = None,
        provider_name: str = "openai",
        model: str = "gpt-4o-mini",
        decision_prompt: str = "",
        include_signal_state: bool = True,
        include_queue_candidates: bool = True,
        include_world_state: bool = False,
        approach_distance: float = 90.0,
        release_distance: float = 110.0,
        red_hold_ticks: int = 3,
        initial_green: bool = True,
        period_ticks: int = 5,
    ):
        if provider is None:
            provider = self._provider_for_name(provider_name)
        self.provider = provider
        self.provider_name = provider_name
        self.model = model
        self.decision_prompt = decision_prompt
        self.include_signal_state = include_signal_state
        self.include_queue_candidates = include_queue_candidates
        self.include_world_state = include_world_state
        self.approach_distance = approach_distance
        self.release_distance = release_distance
        self.red_hold_ticks = red_hold_ticks
        solver = BaseLLMQueueSignalAgent(
            provider,
            model=model,
            decision_prompt=decision_prompt,
            include_signal_state=include_signal_state,
            include_queue_candidates=include_queue_candidates,
            include_world_state=include_world_state,
            approach_distance=approach_distance,
            release_distance=release_distance,
            red_hold_ticks=red_hold_ticks,
        )
        super().__init__(
            id,
            position,
            controls=controls,
            initial_green=initial_green,
            period_ticks=period_ticks,
            label=label,
            solver=solver,
        )

    @staticmethod
    def _provider_for_name(provider_name: str) -> BaseLLMProvider:
        if provider_name == "openai":
            from metrogym.primitives.signal.extras.llm_signal_queue_providers.openai import OpenAIELLProvider

            return OpenAIELLProvider()
        raise ValueError(f"Unsupported LLM provider: {provider_name!r}")
