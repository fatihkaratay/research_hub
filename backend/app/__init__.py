"""Package init — runs before any app.* module.

TLS trust setup. This machine's shell sets SSL_CERT_FILE to a JHU APL root
CA (for the APL network), which makes Python distrust every public site —
all HTTPS calls fail with CERTIFICATE_VERIFY_FAILED. And without any
SSL_CERT_FILE, Homebrew Python can't find a CA bundle at all.

Fix: build a combined bundle (certifi's public CAs + any user-provided CA)
in data/ca-bundle.pem and point this process at it. Must happen before
litellm/openai/httpx are imported — they build their SSL context at import.
"""

import os
from pathlib import Path

import certifi

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _setup_ca_bundle() -> None:
    user_ca = os.environ.get("SSL_CERT_FILE")
    certifi_bundle = Path(certifi.where())

    if not user_ca or not Path(user_ca).is_file() or Path(user_ca) == certifi_bundle:
        os.environ["SSL_CERT_FILE"] = str(certifi_bundle)
        return

    combined = _REPO_ROOT / "data" / "ca-bundle.pem"
    combined.parent.mkdir(exist_ok=True)
    combined.write_bytes(
        certifi_bundle.read_bytes() + b"\n" + Path(user_ca).read_bytes()
    )
    os.environ["SSL_CERT_FILE"] = str(combined)


_setup_ca_bundle()
