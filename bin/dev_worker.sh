#!/usr/bin/env ash
# This runs the worker on periodic burst mode so that changes made to taskse
# during development will be applied when the worker executes them
while true; do
    python /app/manage.py rqworker --burst
    sleep 10
done
