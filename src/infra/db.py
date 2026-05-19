import os
from typing import Optional, Tuple

import pymssql
from dotenv import load_dotenv

load_dotenv()


def _get_database_settings() -> Tuple[str, int, str, str, str]:
    server = os.getenv("DB_SERVER")
    port_raw = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")

    missing = [
        env_name
        for env_name, env_value in (
            ("DB_SERVER", server),
            ("DB_PORT", port_raw),
            ("DB_NAME", database),
            ("DB_USERNAME", username),
            ("DB_PASSWORD", password),
        )
        if not env_value
    ]
    if missing:
        missing_envs = ", ".join(missing)
        raise RuntimeError(
            f"Missing database environment variables: {missing_envs}"
        )

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise RuntimeError("DB_PORT must be a valid integer") from exc

    return server, port, database, username, password


def get_connection():
    server, port, database, username, password = _get_database_settings()

    try:
        return pymssql.connect(
            server=server,
            port=port,
            user=username,
            password=password,
            database=database,
            login_timeout=5,
            timeout=30,
        )
    except Exception as exc:
        raise RuntimeError("Error connecting to SQL Server") from exc


def run_query(sql: str, params: Optional[tuple] = None):
    conn = get_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        if params is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)

        if cursor.description is None:
            return []

        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
