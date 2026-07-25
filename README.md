# The Center for Haptic Audio Interaction Research — Firmware Updater

Browser-based WebUSB DFU flashing tool. Fully static — no server, no backend.
Chrome/Edge only. Must be served over `https://` or `http://localhost`
(GitHub Pages gives you HTTPS automatically).

## Layout

```
index.html              the updater page
releases.json            manifest listing available releases (generated)
releases/                the actual .bin files
scripts/generate-manifest.py   regenerates releases.json from releases/
```

## Run it locally

Any static file server works, e.g.:

```
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Publishing a new release

1. Drop the `.bin` file your existing build step produces (git-describe
   filename + `dfu-suffix` applied) into `releases/`.
2. Regenerate the manifest: `python3 scripts/generate-manifest.py`
3. Commit `releases/<file>.bin` and the updated `releases.json`, then push.

If deployed via GitHub Pages, the site redeploys automatically on push —
usually live within a minute.

Clients can also upload their own `.bin` manually from the page itself if you
don't want to publish through the manifest for a given build.

### Deploying to GitHub Pages

This repo is served as a public github page at [https://chairaudio.github.io/CHAIR-browser-dfu/](https://chairaudio.github.io/CHAIR-browser-dfu/).
This tool needs WebUSB, available in Chrome, Edge, and other Chromium-based browsers (not Firefox or Safari).

## Calibration data protection

Client units carry calibration data in flash from page 253 onward. VID/PID,
flash address, page size, and the reserved page number are hardcoded constants
at the top of `index.html`'s script (not exposed in the UI — this build is
client-facing and shouldn't ask anyone to touch DFU internals). The updater:

- Always erases before writing — there's no "skip erase" option. Un-erased
  NOR flash can only have bits cleared, not set, so writing over stale data
  silently corrupts the image (this bit us in testing — corrupted the vector
  table and left the device stuck in the bootloader).
- Computes how many flash pages the firmware image needs from `PAGE_SIZE`
  and only erases pages
  `0` through `neededPages - 1`.
- Refuses to erase or write at all if the image would reach `RESERVED_PAGE`
  (253) or beyond.

Mass erase is intentionally not offered in this client-facing build, since it
would wipe the whole chip including calibration data.

To change any of these values (different device, different flash layout),
edit the constants block near the top of the `<script>` in `index.html`.

## No live version check

The module's DFU bootloader doesn't expose a running firmware version, so the
updater can't compare "installed" vs "available" automatically — it just lists
what's published and lets the client pick.
