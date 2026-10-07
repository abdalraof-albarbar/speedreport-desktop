"""Portable Windows launcher for the Speed Report web app. Double-click the .exe: it starts the app on this PC
(127.0.0.1 only, no sign-in) and opens it in the default browser. It quits by itself a minute after the last
browser tab is closed. Readings, screenshots and reports are kept in a SpeedReport-data folder next to the .exe.

    SpeedReport.exe                  normal start
    SpeedReport.exe --selftest OUT   start, check the app and the OCR engine, write the result to OUT, exit
"""
import json
import os
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

PORT = 8765
FROZEN = getattr(sys, "frozen", False)
HERE = Path(sys.executable).parent if FROZEN else Path(__file__).resolve().parent
BUNDLE = Path(getattr(sys, "_MEIPASS", HERE))  # where PyInstaller unpacked config.public.json etc.
if not FROZEN:  # running from a checkout: the app source sits in ./app
    sys.path.insert(0, str(HERE / "app"))


def data_home() -> Path:
    """SpeedReport-data next to the .exe (portable); falls back to %LOCALAPPDATA% if that folder is read-only."""
    for base in (HERE, Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "SpeedReport"):
        try:
            home = base / "SpeedReport-data"
            home.mkdir(parents=True, exist_ok=True)
            (home / ".w").write_text("x")
            (home / ".w").unlink()
            return home
        except OSError:
            continue
    raise SystemExit("No writable folder found for the data.")


def load_config(home: Path):
    from speedreport import config
    user_cfg = home / "config.json"          # editable by the user; created from the bundled default on first run
    if not user_cfg.exists():
        user_cfg.write_text((BUNDLE / "config.public.json").read_text(encoding="utf-8"), encoding="utf-8")
    cfg = config.load(user_cfg)
    cfg.data_dir, cfg.reports_dir = home / "data", home / "reports"
    cfg.backup = {"enabled": False}
    cfg.download_url = ""
    return cfg


def already_running() -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/ping", timeout=1.5) as r:
            return r.read() == b"ok"
    except OSError:
        return False


def free_port(preferred: int) -> int:
    for p in (preferred, 0):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", p))
                return s.getsockname()[1]
            except OSError:
                continue
    raise SystemExit("No free port.")


def selftest(out: Path, home: Path) -> int:
    lines, ok = [], True

    def step(name, fn):
        nonlocal ok
        try:
            lines.append(f"OK    {name}: {fn()}")
        except Exception as e:  # report every failure, not just the first
            ok = False
            lines.append(f"FAIL  {name}: {e!r}")

    from PIL import Image
    from speedreport import ocr
    from speedreport.web.app import create_app
    os.environ["SPEEDREPORT_NOAUTH"] = "1"
    app = create_app(load_config(home))
    c = app.test_client()
    step("page", lambda: c.get("/", base_url="http://127.0.0.1").status_code == 200 or (_ for _ in ()).throw(AssertionError("status")))
    step("week", lambda: c.get("/week", base_url="http://127.0.0.1").get_json()["first"])
    step("static image", lambda: len(c.get("/static/desert.png", base_url="http://127.0.0.1").data))
    step("ocr engine loads", lambda: ocr.read_image(Image.new("RGB", (640, 360), "white"))[0].complete())
    out.write_text("\n".join(lines) + ("\nSELFTEST OK\n" if ok else "\nSELFTEST FAILED\n"), encoding="utf-8")
    return 0 if ok else 1


def main() -> int:
    home = data_home()
    if "--selftest" in sys.argv:
        return selftest(Path(sys.argv[sys.argv.index("--selftest") + 1]), home)
    if already_running():                    # a second double-click just brings up the open app
        webbrowser.open(f"http://127.0.0.1:{PORT}/")
        return 0
    log = open(home / "speedreport.log", "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stderr = log            # no console window: keep any output in the log file
    os.environ["SPEEDREPORT_NOAUTH"] = "1"
    from werkzeug.serving import make_server
    from speedreport.web.app import create_app
    app = create_app(load_config(home))
    port = free_port(PORT)
    server = make_server("127.0.0.1", port, app, threaded=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    webbrowser.open(f"http://127.0.0.1:{port}/")
    started = time.time()
    while True:                              # stop when no browser tab has pinged for a minute
        time.sleep(5)
        last = app.config.get("LAST_PING")
        if (last and time.time() - last > 60) or (not last and time.time() - started > 120):
            break
    server.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
