from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_PATH)


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=str(_ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    es_host: str = "http://localhost:9200"
    index_name: str = "clinical_trials"
    data_dir: str = "data"
    clinical_trials_json: str = "clinical_trials.json"


settings = Settings()

ES_HOST = settings.es_host
INDEX_NAME = settings.index_name
DATA_DIR = settings.data_dir
CLINICAL_TRIALS_JSON = settings.clinical_trials_json