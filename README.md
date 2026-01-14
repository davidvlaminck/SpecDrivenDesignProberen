# SpecDrivenDesignProberen

Prototype workspace for a QGIS plugin (PyQGIS) developed using spec-driven, phased iterations.

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

