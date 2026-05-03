from __future__ import annotations

from beartype import beartype


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
        for key, value in params.items():
            if not hasattr(self, key):
                raise ValueError(f"Invalid parameter {key!r} for {type(self).__name__}")
            setattr(self, key, value)
        return self
