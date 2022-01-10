import secrets
from typing import Any, Dict, List, Optional, Union

import dotenv
from pydantic import AnyHttpUrl, AnyUrl, BaseSettings, validator

# Load Enviroment Variables
dotenv.load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    BACKEND_CORS_ORIGINS: Union[List[AnyHttpUrl], str] = [
        "http://0.0.0.0:8080",
        "http://0.0.0.0:8000",
        "http://localhost:3000",
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True, allow_reuse=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str):
            if v.startswith("["):
                v = v[1 : len(v) - 1]
            if v.endswith("]"):
                v = v[: len(v) - 2]
            return [i.strip().replace('"', "").replace("'", "") for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    MYSQL_SERVER: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[AnyUrl] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return AnyUrl.build(
            scheme="mysql+pymysql",
            user=values.get("MYSQL_USER"),
            password=values.get("MYSQL_PASSWORD"),
            host=values.get("MYSQL_SERVER"),
            path=f"/{values.get('MYSQL_DB') or ''}",
            port=values.get("MYSQL_PORT"),
        )

    CELERY_BROKER_URL: str

    class Config:
        case_sensitive = True


settings = Settings()
