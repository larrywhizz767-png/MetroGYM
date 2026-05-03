from __future__ import annotations

import threading
import time

from demo import build_system


def main() -> None:
    system = build_system(tick_ms=300, render_scale=1).fit()

    def auto_close() -> None:
        time.sleep(5)
        print("[smoke] closing window")
        system.simulator.close()

    threading.Thread(target=auto_close, daemon=True).start()
    system.run()
    print("[smoke] clean exit")


if __name__ == "__main__":
    main()
