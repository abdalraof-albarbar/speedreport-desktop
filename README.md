# Speed Report for Windows (portable .exe)

Weekly Internet Test · Communications Department · Akakus Oil Operations, El Sharara Field.

**Download:** [SpeedReport.exe](../../releases/latest/download/SpeedReport.exe) (latest release). No installer and no account needed.

1. Download `SpeedReport.exe` anywhere (Desktop, a USB stick, ...).
2. Double-click it. Windows may show "Windows protected your PC" because the file is not code-signed: choose **More info → Run anyway**.
3. The app opens in your browser at `http://127.0.0.1:8765`. It runs only on your PC and needs no sign-in.
4. It closes itself about a minute after you close the browser tab. Double-clicking again re-opens it.

Your readings, screenshots and reports are saved in a **`SpeedReport-data`** folder next to the .exe (copy that folder to move to another PC).
`SpeedReport-data\config.json` holds the settings (engineer name, SLA values, site list...); edit it with Notepad.
The weekly e-mail and the GitHub backup are turned off in this version.

## How this repo works (CI/CD)

This repo contains only the launcher and the build pipeline. The application source stays in the private repo
`abdalraof-albarbar/weekly-internet-test-report`, which the pipeline reads with a read-only deploy key
(secret `SOURCE_DEPLOY_KEY`).

| Trigger | What happens |
|---|---|
| every day 03:17 UTC | if the source repo has new commits, build + publish a new release; otherwise do nothing |
| **Actions → build-exe → Run workflow** | always builds and publishes |
| push a tag `v*` | builds and publishes |

The build (GitHub Actions, `windows-latest`): check out the source → PyInstaller one-file build → self-test the exe
(`SpeedReport.exe --selftest`: the app starts, pages load, the OCR engine loads) → SHA-256 → GitHub Release
(5 newest releases are kept). Local build: clone the source repo into `app/`, then run `./build.ps1`.
