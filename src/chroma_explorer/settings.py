from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True, env_prefix="CHROMA_EXPLORER_")
    path: str | None = Field(default=None)


if __name__ == "__main__":
    settings = Settings()
    print(settings)
