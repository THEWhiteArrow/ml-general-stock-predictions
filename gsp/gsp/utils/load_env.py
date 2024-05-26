import os
from dotenv import load_dotenv
from typing import Optional


def load_env_variables() -> tuple[str, str, str, str]:
    load_dotenv()

    db_user: Optional[str] = os.getenv("DB_USER")
    db_password: Optional[str] = os.getenv("DB_PASSWORD")
    cluster_name: Optional[str] = os.getenv("CLUSTER_NAME")
    db_name: Optional[str] = os.getenv("DB_NAME")

    if not db_user or not db_password or not cluster_name or not db_name:
        raise Exception("Please provide DB_USER, DB_PASSWORD, CLUSTER_NAME, and DB_NAME in your .env file")

    return db_user, db_password, cluster_name, db_name
