"""Render the actual portfolio ident canvas as a 15-second GitHub profile GIF.

Requires Playwright, Chromium, and FFmpeg. See scripts/README.md.
"""

import argparse
import base64
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import shutil
import subprocess
import tempfile
from threading import Thread
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
DURATION = 15


@contextmanager
def serve_source():
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(ROOT)))
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/profile-ident.html?render"
    finally:
        server.shutdown()
        server.server_close()
        worker.join()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "assets/hero.gif")
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--fps", type=int, choices=(5, 10, 20, 25, 50), default=10)
    parser.add_argument("--browser", default=shutil.which("chromium"))
    args = parser.parse_args()
    if args.width < 16 or args.width % 16:
        parser.error("--width must be a positive multiple of 16")
    if not shutil.which("ffmpeg"):
        parser.error("FFmpeg is required")

    output = args.output.resolve()
    height = args.width * 9 // 16
    frame_count = DURATION * args.fps
    with tempfile.TemporaryDirectory(prefix="74hamed-ident-") as directory:
        frames = Path(directory)
        with serve_source() as source_url, sync_playwright() as playwright:
            launch = {"headless": True}
            if args.browser:
                launch["executable_path"] = args.browser
            browser = playwright.chromium.launch(**launch)
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(source_url)
            page.wait_for_function("window.profileIdent?.ready === true")
            assert page.evaluate('document.fonts.check(\'800 40px "JetBrains Mono"\')'), "Font failed to load"
            page.evaluate("""([width, height]) => {
                window.exportCanvas = document.createElement('canvas');
                exportCanvas.width = width;
                exportCanvas.height = height;
            }""", [args.width, height])
            for index in range(frame_count):
                # A readable first frame also works as a static preview.
                time = 13.6 if index == 0 else index / args.fps
                encoded = page.evaluate("""time => {
                    profileIdent.render(time);
                    exportCanvas.getContext('2d').drawImage(document.getElementById('c'),
                        0, 0, exportCanvas.width, exportCanvas.height);
                    return exportCanvas.toDataURL('image/png').split(',')[1];
                }""", time)
                (frames / f"{index:04d}.png").write_bytes(base64.b64decode(encoded))
                if index % args.fps == 0:
                    print(f"Rendered {index // args.fps + 1}/{DURATION} seconds", flush=True)
            browser.close()
            if errors:
                raise RuntimeError("Browser errors: " + "; ".join(errors))

        common = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                  "-framerate", str(args.fps), "-i", str(frames / "%04d.png")]
        palette = frames / "palette.png"
        subprocess.run(common + ["-vf", "palettegen=max_colors=96:reserve_transparent=0",
                                 "-frames:v", "1", str(palette)], check=True)
        generated = frames / "hero.gif"
        subprocess.run(common + ["-i", str(palette), "-lavfi", "paletteuse=dither=none",
                                 "-loop", "0", str(generated)], check=True)
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(generated, output)
        shutil.copyfile(frames / "0000.png", output.with_name(f"{output.stem}-poster.png"))
    print(f"Generated {output} ({frame_count} frames, {DURATION}s, {output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
