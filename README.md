# Ctrlable DALI

Ctrlable Pro sidebar panel for the **dali-bridge** (`python-dali` + hasseb DALI
master, running in its own LXC). Mirrors the Ctrlable **art-net** panel pattern:
a custom sidebar panel → thin custom element → iframe → standalone vanilla-JS UI,
talking to a websocket API that **bridges to the dali-bridge over MQTT**.

Unlike art-net (engine runs in HA), the DALI engine is remote in the LXC, so the
component's WebSocket handlers publish to the bridge's MQTT topics and serve a
cached view of its retained state — no hardware access in HA.

## Architecture

```
dali-app.html (vanilla JS) ─postMessage─▶ ctrlable-dali-panel.js ─callWS─▶
  ctrlable_dali (WS API) ─mqtt.async_publish/subscribe─▶ dali-bridge (LXC) ─▶ DALI bus
```

## WebSocket ↔ MQTT map

| WS command | MQTT topic |
|---|---|
| `ctrlable_dali/state` | (cached from `dali/#` retained topics) |
| `ctrlable_dali/commission` | `dali/config/commission` |
| `ctrlable_dali/scan` | `dali/config/scan` |
| `ctrlable_dali/group_set` | `dali/config/group/set` |
| `ctrlable_dali/scene_store` | `dali/config/scene/store` |
| `ctrlable_dali/scene_recall` | `dali/config/scene/recall` |
| `ctrlable_dali/light_set` | `dali/light/<target>/set` |
| `ctrlable_dali/raw` | `dali/cmd/send` (reply cached from `dali/cmd/res`) |

## Panel screens (v1)
Bridge status · Devices · Groups matrix (0–15) · Scenes (store/recall) ·
Colour (DT8 Tc) · Raw frame console.

## Install (dev)
Copy `custom_components/ctrlable_dali/` into HA `/config/custom_components/`,
restart HA, add the **Ctrlable DALI** integration (needs the MQTT integration
configured against the same broker as the bridge). Panel appears in the sidebar.

Open `custom_components/ctrlable_dali/panel/dali-app.html` directly in a browser
for a standalone design preview (seed data).

## Repos (two-repo model)
- **Private source repo** (this one): all plain source, the RSA key stays out of it
  (only the public key is embedded), the `tools/gate_build/` tooling, and the CI
  workflow. HACS does **not** install from here.
- **Public dist repo** (`PUBLIC_REPO` = `Ctrlable/ctrlable-dali`): receives
  only the CI-built artifact — per-arch native `abi3.so`, arch-shim `.py` stand-ins,
  minified Python, obfuscated panel JS, minified HTML. **HACS installs from here.**
  Plain source never leaves the private repo.

## Device & sidebar
The integration creates a **"Ctrlable Dali"** device (Settings → Devices) carrying a
**"Show in sidebar"** switch (`EntityCategory.CONFIG`, off by default). The panel URL is
always served; the sidebar link appears only when the switch is on. The device page's
link opens the panel regardless.

## Licensing & protection (phase 3)
- **License gate** (`license.py`): RS256 JWT verified offline against the embedded
  portal public key + daily online revocation + offline grace + optional HA-instance
  binding + expiry modes (`disable`/`grace_period`/`warn_only`). `EXPECTED_PRODUCT="ctrlable_dali"`.
  The panel always loads (to enter a license); the **action** WS commands
  (commission / group / scene / light / raw) are gated. Read-only `state` and
  `license_*` are always available.
- **Before release:** replace `_PUBLIC_KEY` in `license.py` with the `ctrlable_dali`
  product public key from portal.ctrlable.com (until then, no license validates).
- **CI** (`.github/workflows/hacs-release.yml`): on a `vX.Y.Z` tag — Cython-compiles
  `license/_impl/config_flow/websocket_api/const` to per-arch `abi3.so` (loaded via
  `tools/gate_build/arch_shim.py`), minifies remaining Python, obfuscates panel JS
  (`javascript-obfuscator`), minifies HTML, and publishes only the built artifact to
  the public HACS repo (`PUBLIC_REPO` + secret `PUBLIC_REPO_TOKEN`). Plain source
  stays private; `workflow_dispatch` = dry-run artifact.

## Roadmap
- [x] v1 panel + WS↔MQTT bridge
- [x] Licensing (RS256 JWT gate) + panel license UI + gated action commands
- [x] CI: Cython abi3 gate + JS obfuscation + HTML minify → public HACS repo
- [ ] Embed the real portal public key; first tagged release
- [ ] Per-device naming, scene-level read-back, DT8 RGB once verified on gear
