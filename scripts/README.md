# Profile ident

`../profile-ident.html` is the supplied 15-second canvas ident, with its JetBrains
Mono font stored locally under `../assets/fonts/`. Open that HTML file in a browser
to play the original animation with sound, replay it, or export a WebM.

GitHub profile READMEs cannot run canvas JavaScript or play embedded audio. The
README therefore uses `../assets/hero.gif`, rendered directly from that HTML.
The GIF loops for 15 seconds at 960×540 and 10 fps. Its first frame shows the final
contact scene so a static preview still identifies the profile. The font's OFL
license is included beside the font.

## Regenerate the GIF

Use Python 3.10 or newer, FFmpeg, and Chromium. In the prepared cloud environment,
FFmpeg and `/usr/bin/chromium` are already available.

From the repository root, install the Python dependency in a virtual environment
outside the checkout if it is not already available:

```sh
python3 -m venv /tmp/74hamed-profile-venv
/tmp/74hamed-profile-venv/bin/python -m pip install -r scripts/requirements.txt
/tmp/74hamed-profile-venv/bin/python scripts/generate_profile_hero.py
```

If Chromium is not installed on your system, install Playwright's browser using
`python -m playwright install chromium` in that virtual environment. The exporter
uses system Chromium when present and Playwright's Chromium otherwise. FFmpeg must
be on `PATH`.

With the dependencies already installed:

```sh
python3 scripts/generate_profile_hero.py
```

The script resolves its HTML source relative to itself, so it also works from
another working directory. To keep an existing GIF while checking a new render:

```sh
python3 scripts/generate_profile_hero.py --output /tmp/74hamed-preview.gif
```

The exporter serves the source on a temporary loopback HTTP server, which stops
when rendering finishes. Frames and palettes are generated in a temporary
directory and removed after export. The final GIF and its still image
(`hero-poster.png` by default) are written after rendering and encoding succeed.
