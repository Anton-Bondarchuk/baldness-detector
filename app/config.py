from enum import Enum
from typing import Optional
from pydantic import SecretStr, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

# class LoggingRenderer(str, Enum):
#     JSON = "JSON"
#     CONSOLE = "CONSOLE"

# class LoggingSettings(BaseSettings):
#     level: str = "INFO"
#     format: str = "%Y-%m-%d %H:%M:%S"
#     is_utc: bool = False
#     renderer: LoggingRenderer = LoggingRenderer.JSON
#     log_unhandled: bool = False

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         env_prefix="LOGGING_",
#         extra="allow",
#     )

class GoogleOAuthSettings(BaseSettings):
    client_id: str = "your-google-client-id"
    client_secret: SecretStr 
    conf_url: HttpUrl = "https://accounts.google.com/.well-known/openid-configuration"
    redirect_uri: Optional[HttpUrl] = 'http://localhost:8000/auth/callback'
    scope: str = "openid email profile"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="GOOGLE_OAUTH_",
        extra="allow",
    )

class AppSettings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    hot_reload: bool = False
    secret_key: SecretStr
    debug: bool = False
    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    # allowed_hosts: list[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="allow",
    )

class DatabaseSettings(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: SecretStr
    database: str = "baldness_detector"
    sql_echo: bool = False
    
    @property
    def sqlalchemy_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.database}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DB_",
        extra="allow",
    )

# class BaldnessAPISettings(BaseSettings):
#     api_version: str = "v1"
#     ml_model_path: Optional[str] = None
#     upload_folder: str = "./uploads"
    
#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         env_prefix="BALDNESS_API_",
#         extra="allow",
#     )

google_oauth_config = GoogleOAuthSettings()
app_config = AppSettings()
db_config = DatabaseSettings()

# Create config instances
# log_config = LoggingSettings()
# baldness_api_config = BaldnessAPISettings()