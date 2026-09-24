from collections.abc import MutableMapping
from typing import Any

_entitlements: dict[str, dict[str, Any]] = {}


def get_entitlements_store() -> MutableMapping[str, dict[str, Any]]:
    return _entitlements


def reset_entitlements_store() -> None:
    _entitlements.clear()
