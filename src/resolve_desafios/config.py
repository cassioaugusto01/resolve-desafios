import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Settings:
    openai_api_key: Optional[str]
    openai_model: str
    db_path: Path
    app_language: str


_CACHED_SETTINGS: Optional[Settings] = None


def _coalesce_env_str(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value


def get_settings() -> Settings:
    global _CACHED_SETTINGS
    if _CACHED_SETTINGS is not None:
        return _CACHED_SETTINGS

    load_dotenv(override=False)

    openai_api_key = _coalesce_env_str("OPENAI_API_KEY")
    openai_model = _coalesce_env_str("OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini"
    db_path_env = _coalesce_env_str("RESOLVE_DB_PATH", "./data/resolve_desafios.db") or "./data/resolve_desafios.db"
    app_language = _coalesce_env_str("APP_LANGUAGE", "pt-BR") or "pt-BR"

    db_path = Path(db_path_env).expanduser().resolve()
    ensure_app_dirs(db_path)

    _CACHED_SETTINGS = Settings(
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        db_path=db_path,
        app_language=app_language,
    )
    return _CACHED_SETTINGS


def ensure_app_dirs(db_path: Path) -> None:
    data_dir = db_path.parent
    data_dir.mkdir(parents=True, exist_ok=True)


