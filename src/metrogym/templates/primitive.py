from __future__ import annotations

from beartype import beartype

from metrogym.validation import validation_registry


@beartype
class BaseMetroPrimitive:
    primitive_group = "generic"

    @beartype
    def fit(self, context: object) -> "BaseMetroPrimitive":
        return self

    @beartype
    def transform(self, context: object) -> object:
        return context

    @beartype
    def fit_transform(self, context: object) -> object:
        self.fit(context)
        return self.transform(context)

    @beartype
    def get_params(self, deep: bool = True) -> dict[str, object]:
        return {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        }

    @beartype
    def set_params(self, **params: object) -> "BaseMetroPrimitive":
        registry = validation_registry()
        for key, value in params.items():
            if not hasattr(self, key):
                registry.raise_issue(registry.system_issue("invalid_system_param", path=f"{type(self).__name__}.{key}", param=key))
            setattr(self, key, value)
        return self
