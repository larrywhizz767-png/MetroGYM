from __future__ import annotations

"""Public renderer primitive for configuring MetroGYM visual output."""

from beartype import beartype

from metrogym.templates.primitive import BaseMetroPrimitive


@beartype
class MetroGYMRenderer(BaseMetroPrimitive):
    """Declare renderer configuration inside a MetroGYM pipeline.

    The renderer primitive does not create runtime objects by itself. Instead,
    it carries rendering preferences, such as a panel scale override, that are
    read by ``metrogym.MetroSystem`` while fitting the world. It is optional and
    only needs to be added when the user wants to control renderer-specific
    parameters from the pipeline.

    Args:
        scale (int | float | None, default=None):
            Optional renderer scale override. If omitted, the system-level
            ``render_scale`` is used.

    Attributes:
        scale (int | float | None):
            Optional renderer scale override.

    Examples:
        !!! example "Use `MetroGYMRenderer` only when renderer settings matter"

            ```python hl_lines="11"
            from metrogym import Color, MetroSystem, train
            from metrogym.primitives import Line, Network, Station, Train
            from metrogym.rendering import MetroGYMRenderer

            system = MetroSystem(name="Renderer Demo").pipeline([
                Network([
                    Line("Loop", Color.BLUE, [(120, 120), (420, 120), (420, 320), (120, 320), (120, 120)]),
                    Station("Origin", (120, 120)),
                    Station("East", (420, 120)),
                ]),
                MetroGYMRenderer(scale=3),
                Train("A", line="Loop", solver=train.always_proceed()),
            ])

            system.fit().run()
            ```

            Add the renderer primitive only when you want to override renderer
            settings such as the pipeline-level scale.
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
