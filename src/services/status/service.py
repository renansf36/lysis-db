from ...infra.db import run_query

def get_db_status():
  try:
    run_query("SELECT 1 AS ok")

    version = run_query("SELECT @@VERSION AS version")
    db_name = run_query("SELECT DB_NAME() AS database_name")
    user = run_query("SELECT SYSTEM_USER AS user_name")

    return {
      "status": "online",
      "database": db_name[0]["database_name"],
      "current_user": user[0]["user_name"],
      "version": version[0]["version"],
    }

  except Exception as e:
    return {
      "status": "offline",
      "error": str(e)
    }
