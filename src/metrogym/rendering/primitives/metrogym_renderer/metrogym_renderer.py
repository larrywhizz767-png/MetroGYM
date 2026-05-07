from __future__ import annotations

"""Public renderer primitive for configuring MetroGYM visual output."""

from beartype import beartype

from metrogym.templates.primitive import BaseMetroPrimitive


@beartype
class MetroGYMRenderer(BaseMetroPrimitive):
    """Declare renderer configuration inside a MetroGYM pipeline.

    The renderer primitive does not create runtime objects by itself. Instead,
    it carries rendering preferences, such as a panel scale override, that are
    read by :class:`metrogym.MetroSystem` while fitting the world.

    Args:
        scale (int | float | None, default=None):
            Optional renderer scale override. If omitted, the system-level
            ``render_scale`` is used.

    Attributes:
        scale (int | float | None):
            Optional renderer scale override.
    """

    primitive_group = "rendering"

    @beartype
    def __init__(self, *, scale: int | float | None = None):
        self.scale = scale

    @beartype
    def transform(self, context: object) -> object:
        """Pass the build context through unchanged.

        Args:
            context (object):
                Build context being materialised during ``fit``.

        Returns:
            object:
                Unmodified build context.
        """
        return context
