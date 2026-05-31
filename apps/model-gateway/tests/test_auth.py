from src.dependencies.auth import extract_api_key


def test_extract_api_key_prefers_x_api_key() -> None:
    api_key = extract_api_key(
        x_api_key="sk-header",
        authorization="Bearer sk-bearer",
    )

    assert api_key == "sk-header"


def test_extract_api_key_accepts_bearer_token() -> None:
    api_key = extract_api_key(
        x_api_key=None,
        authorization="Bearer sk-bearer",
    )

    assert api_key == "sk-bearer"


def test_extract_api_key_ignores_non_bearer_authorization() -> None:
    api_key = extract_api_key(
        x_api_key=None,
        authorization="Basic abc",
    )

    assert api_key is None
