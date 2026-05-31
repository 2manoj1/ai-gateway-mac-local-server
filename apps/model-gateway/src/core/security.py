from hashlib import sha256
from hmac import compare_digest


def api_keys_match(candidate: str | None, expected: str) -> bool:
    if not candidate:
        return False

    return compare_digest(candidate, expected)


def hash_api_key(api_key: str) -> str:
    return sha256(api_key.encode("utf-8")).hexdigest()
