from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    ORIGIN: SecretStr
    ARCHIVE: SecretStr
    VACANCIES: SecretStr
    MEMES: SecretStr
    FILES: SecretStr
    PAPERS: SecretStr
    COURSES: SecretStr
    DEFAULT_DB_NAME: SecretStr
    DB_USER: SecretStr
    DB_PASSWORD: SecretStr
    DB_HOST: SecretStr
    DB_PORT: SecretStr
    DB_NAME: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='ascii')

config = Settings()