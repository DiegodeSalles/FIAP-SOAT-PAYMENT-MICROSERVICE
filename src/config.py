from functools import lru_cache
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str = Field(..., validation_alias="MONGODB_URL", description="MongoDB connection URL")
    mongodb_db_name: str = Field(..., validation_alias="MONGODB_DB_NAME", description="MongoDB database name")
    mp_access_token: str = Field(..., validation_alias="MP_ACCESS_TOKEN", description="MercadoPago Access Token")
    mp_base_url: str = Field("https://api.mercadopago.com", validation_alias="MP_BASE_URL", description="MercadoPago API Base URL")
    mp_pos_id: str = Field(..., validation_alias="MP_POS_ID", description="MercadoPago POS ID")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

@lru_cache()
def get_settings() -> Settings:
    return Settings()