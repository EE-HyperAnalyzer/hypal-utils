import hashlib
import json
import platform


def get_device_fingerprint() -> str:
    fingerprint_data = {
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }

    fingerprint_string = json.dumps(
        fingerprint_data, sort_keys=True, separators=(",", ":")
    )

    fingerprint_hash = hashlib.sha256(fingerprint_string.encode("utf-8")).hexdigest()

    return fingerprint_hash
