from typing import NotRequired, TypedDict, Unpack

from pydantic import Field
from pydantic_settings import BaseSettings, CliPositionalArg, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True, env_prefix="CHROMA_EXPLORER_")
    path: CliPositionalArg[str | None] = Field(default=None)


class SettingsKwargs(TypedDict):
    path: NotRequired[str | None]


_settings = Settings()


def get_settings() -> Settings:
    return _settings


def edit_settings(**kwargs: Unpack[SettingsKwargs]) -> Settings:
    global _settings
    _settings = Settings(**{**_settings.model_dump(), **kwargs})
    return _settings
