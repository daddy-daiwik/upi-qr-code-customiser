"""Unit tests for normalize_upi_uri (pure-Python, no browser deps needed)."""

import sys
import types
import unittest

# Stub out browser-only imports so the module can be imported outside Pyodide
for mod in ("js", "pyodide", "pyodide.ffi", "segno"):
    if mod not in sys.modules:
        stub = types.ModuleType(mod)
        sys.modules[mod] = stub

# Provide minimal stubs expected at module level
js_stub = sys.modules["js"]
for attr in ("document", "console", "Uint8Array", "window", "FileReader", "Image",
             "jsQR", "Object"):
    setattr(js_stub, attr, None)

pyodide_ffi_stub = sys.modules["pyodide.ffi"]
pyodide_ffi_stub.create_proxy = lambda f: f  # type: ignore[attr-defined]

# Now we can safely import the app; DOM calls at module level will fail but
# the function we need is defined before any DOM access.
import importlib.util, pathlib

_spec = importlib.util.spec_from_file_location(
    "pyscript_app",
    pathlib.Path(__file__).parent / "pyscript_app.py",
)
_mod = importlib.util.module_from_spec(_spec)
try:
    _spec.loader.exec_module(_mod)  # type: ignore[union-attr]
except Exception:
    pass  # DOM calls at the bottom will raise; the function is already defined

normalize_upi_uri = _mod.normalize_upi_uri


class TestNormalizeUpiUri(unittest.TestCase):

    def test_strips_extra_params(self):
        raw = "upi://pay?pa=9000000000@upi&pn=FIRST%20LAST&cu=INR&orgid=XYZ&sign=AAA"
        expected = "upi://pay?pa=9000000000@upi&pn=FIRST%20LAST&cu=INR"
        self.assertEqual(normalize_upi_uri(raw), expected)

    def test_already_minimal_unchanged(self):
        raw = "upi://pay?pa=abc@upi&pn=Test%20User&cu=INR"
        self.assertEqual(normalize_upi_uri(raw), raw)

    def test_no_amount_preserved(self):
        raw = "upi://pay?pa=abc@upi&pn=Name&cu=INR&am=100"
        result = normalize_upi_uri(raw)
        self.assertNotIn("am=", result)

    def test_order_enforced_pa_pn_cu(self):
        raw = "upi://pay?cu=INR&pn=Name&pa=abc@upi"
        result = normalize_upi_uri(raw)
        self.assertEqual(result, "upi://pay?pa=abc@upi&pn=Name&cu=INR")

    def test_non_upi_payload_unchanged(self):
        raw = "https://example.com/some-path?foo=bar"
        self.assertEqual(normalize_upi_uri(raw), raw)

    def test_empty_string(self):
        self.assertEqual(normalize_upi_uri(""), "")

    def test_upi_pay_no_query(self):
        self.assertEqual(normalize_upi_uri("upi://pay"), "upi://pay")

    def test_percent_encoding_preserved(self):
        raw = "upi://pay?pa=test@upi&pn=First%20Last&cu=INR&sign=abc%2Bdef"
        result = normalize_upi_uri(raw)
        self.assertIn("pn=First%20Last", result)
        self.assertNotIn("sign=", result)


if __name__ == "__main__":
    unittest.main()
