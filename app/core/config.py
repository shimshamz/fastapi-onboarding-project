from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # to get a string like this run:
    # openssl rand -hex 32
    SECRET_KEY: str = "f336b53520e71b93e5527ba06e097780ebbb8c6f2364ee4457cfaf571b61657d"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()  # type: ignore