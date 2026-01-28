#!/usr/bin/env python3
import os
import subprocess

port = os.environ.get("PORT", "8000")
subprocess.call(["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", port])
