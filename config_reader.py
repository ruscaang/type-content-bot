from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='ascii')


config = Settings()
print(config.BOT_TOKEN.get_secret_value())
