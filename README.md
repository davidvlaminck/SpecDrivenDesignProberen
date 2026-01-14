# SpecDrivenDesignProberen

Prototype workspace for a QGIS plugin (PyQGIS) developed using spec-driven, phased iterations.

## Phase 0: plugin skeleton (load in QGIS)

This repo now contains a minimal QGIS plugin package at `otlmow_markeringen/`.

### Quick repo-side checks (no QGIS needed)

```bash
python3 scripts/check_plugin_structure.py
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
```

### Try it in QGIS (manual smoke)

1. Copy/symlink the `otlmow_markeringen/` folder into your QGIS plugins directory.
   - Linux (typical): `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - Windows (typical): `%APPDATA%\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\`
   
#### Option A (recommended for dev): add as symlink / junction

This lets you edit the plugin in this repo and immediately test changes in QGIS.

**Linux (bash)**

```bash
# Create the QGIS plugins folder if it doesn't exist
mkdir -p ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins

# Create/update a symlink that points to this repo's plugin folder
ln -sfn "$(pwd)/otlmow_markeringen" \
  ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/otlmow_markeringen
```

**Windows (PowerShell)**

```powershell
# QGIS plugins folder (usually)
$plugins = Join-Path $env:APPDATA 'QGIS\QGIS3\profiles\default\python\plugins'
New-Item -ItemType Directory -Force -Path $plugins | Out-Null

# Create a directory junction (works without needing Developer Mode)
$target = (Resolve-Path .\otlmow_markeringen).Path
cmd /c "mklink /J \"$plugins\otlmow_markeringen\" \"$target\""
```

**Windows (cmd.exe)**

```bat
REM QGIS plugins folder (usually)
set PLUGINS=%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins
if not exist "%PLUGINS%" mkdir "%PLUGINS%"

REM Create a directory junction
mklink /J "%PLUGINS%\otlmow_markeringen" "%CD%\otlmow_markeringen"
```

Notes:
- On Windows, a **junction** (`/J`) is the easiest option and typically doesn't require admin rights.
- If you prefer a real symlink on Windows, use `mklink /D` (often requires admin or Developer Mode).
 
#### Troubleshooting (Windows): “This plugin is broken / no metadata file”

If QGIS shows the plugin in red and claims there is **no metadata file**, it almost always means QGIS can't see a `metadata.txt` **at the plugin root folder level**.

Checklist:
- The plugins folder must contain a directory named **exactly** `otlmow_markeringen`.
- Inside that directory, `metadata.txt` must exist at:
  `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\otlmow_markeringen\metadata.txt`
- Make sure you did **not** end up with a nested folder like `...\otlmow_markeringen\otlmow_markeringen\metadata.txt`.
- Windows sometimes hides file extensions in Explorer. Ensure the file is really named `metadata.txt` (not `metadata.txt.txt`).

Recommended quick check (PowerShell):

```powershell
$p = Join-Path $env:APPDATA 'QGIS\QGIS3\profiles\default\python\plugins\otlmow_markeringen\metadata.txt'
Test-Path $p
Get-Content $p -TotalCount 5
```

After fixing the folder/junction, restart QGIS (the plugin list is cached).
 
Extra debug tip (cross-platform): validate what QGIS *should* see

Run this against the plugin folder that sits inside the QGIS plugins directory:

```powershell
python scripts/validate_qgis_plugin_dir.py \
  "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\otlmow_markeringen"
```

If this script prints `metadata.txt exists: False`, then QGIS will also treat it as missing.
  
2. Start QGIS.
3. Enable the plugin via **Plugins > Manage and Install Plugins**.
4. Click the toolbar button **“OTLMOW: Plugin loaded”**.
   - Expected: a message in the message bar + a log entry in **View > Panels > Log Messages**.

## PyQGIS interpreter setup (Linux)

This repo currently contains only a spec plus small helper scripts.

On Linux Mint/Ubuntu, QGIS installs its Python bindings into the system Python `dist-packages`.
In this environment, PyQGIS was found at:

- `/usr/lib/python3/dist-packages/qgis`

### Quick check

Run the smoke test with the system interpreter:

```bash
/usr/bin/python3 scripts/check_pyqgis.py
```

If `qgis: OK` prints, your interpreter can import PyQGIS.

### PyCharm configuration

In **Settings > Project > Python Interpreter** choose **System Interpreter** and point it to:

- `/usr/bin/python3`

That interpreter should see the QGIS-installed packages.

If you also want a virtualenv for pure-Python unit tests, keep using `.venv`, but note it
won't have PyQGIS unless you deliberately add system site-packages.
