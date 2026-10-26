# Chess

A desktop chess game with human, computer, and computer-vs-computer modes.

## Download and play

Open the repository's [Releases page](https://github.com/GoldenElf58/Chess/releases/latest) and download the archive for
your operating system:

- **Windows:** `Chess-windows-x64.zip`
- **macOS (Apple Silicon):** `Chess-macos-arm64.zip`
- **Linux:** `Chess-linux-x64.zip`

Extract the ZIP file, then launch the included **Play Chess** file (`.bat` on Windows, `.command` on macOS, or `.sh` on
Linux). Keep that launcher beside the `Chess` executable and the `piece_images` folder. The release builds include
Python and the required libraries; you do not need to install Python.

On macOS, if Gatekeeper blocks the app because it is not signed, use **Control-click → Open** on `Play Chess.command`
the first time. On Linux, if needed, allow the script to run with `chmod +x "Play Chess.sh"` and start it from the
extracted folder.

## Run from source

You need Python 3.14. From the repository folder, create and activate a virtual environment, then install the runtime
dependencies:

```bash
python3.14 -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

The optional mypyc native compilation in `build/setup.py` is intended for development/performance experiments; players
do not need it. It compiles in place and may leave platform-specific files in the checkout.

## Build a release locally

> Warning: This is untested and may not work.

Builds must be made on the operating system they target. With the virtual environment active:

On macOS or Linux, use:

```bash
python -m pip install -r requirements-build.txt
PYINSTALLER_CONFIG_DIR=.pyinstaller-cache pyinstaller --noconfirm --onedir --name Chess main.py
```

On Windows PowerShell, use:

```powershell
$env:PYINSTALLER_CONFIG_DIR = ".pyinstaller-cache"
pyinstaller --noconfirm --onedir --name Chess main.py
```

Copy `piece_images/`, `fens.txt`, and the matching launcher from `release/` into `dist/Chess/`, then zip the `Chess`
folder. GitHub Actions performs these steps for Windows x64, macOS Apple Silicon, and Linux x64 whenever a version tag
is pushed.

## Publish a GitHub release

1. Update the version in `pyproject.toml` and commit the change.
2. Create and push a matching version tag, for example:

   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. GitHub Actions builds the three downloadable ZIP files and attaches them to a draft release. Review the build results
4. and publish the draft from the repository's **Releases** page.

The workflow is in `.github/workflows/release.yml`. In **Settings → Actions → General → Workflow permissions**, enable
**Read and write permissions** so GitHub Actions can create and upload the draft release.

### Main Menu Options

- **Options** - Switch to the options menu.
- **Human** - Play against yourself or pass the computer between you and your friend.
- **Play White** - Play against the computer as white.
- **Play Black** - Play against the computer as black.
- **AI vs AI** - Play the computer against itself.
- **Deep Test** - Play the one bot against another bot in 1000 games to see which is better.

### Options Menu Options

- **Main Menu** - Return to the main menu.
- **BotVx** - Click to cycle through the bots to play against (white).
- **BotVx** - Click to cycle through the bots to play against (black).
- **Normal/Test** - Click to switch between normal and test mode.

### Info Meanings

- **Evaluation**: The evaluation the last bot gave of the board (+ is white winning, - is black winning).
- **Turn**: The turn of the game.
- **Time**: The total time you have been in this mode.
- **Depth BotA/B**: The average depth the bot searched to across all games.
- **BotA (W/B)**: How many times Bot A has won and whether they are currently white or black.
- **Draws**: How many draws there have been.
- **BotB (W/B)**: How many times Bot B has won and whether they are currently white or black.
- **P-Value**: The probability that BotA has the same skill as BotB.
