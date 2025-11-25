# run_prod.py
import os
import sys

cmd = ""

if sys.platform.startswith("win"):
  cmd = "uvicorn src.main:app --host 0.0.0.0 --port 4545"
else:
  cmd = (
    "gunicorn -k uvicorn.workers.UvicornWorker"
    "src.main:app --bind 0.0.0.0:4545 --workers 4"
  )

print(f"Running: {cmd}")
os.system(cmd)
