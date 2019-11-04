# This file will be re-written during the Docker build. For development, the
# following defaults are provided.
import subprocess

VERSION = subprocess.check_output(
    ["git", "describe", "--always", "--tags"]
).strip().decode()
COMMIT = subprocess.check_output(
    ["git", "rev-parse", "--short", "HEAD"]
).strip().decode()
