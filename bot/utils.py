import os

def env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in {"1", "true", "yes"}


def env_list(name: str, default: str = "") -> list[str]:
    val = os.getenv(name, default)
    return [v.strip() for v in val.split(",") if v.strip()]

