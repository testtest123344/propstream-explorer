#!/bin/bash
exec gunicorn api.server:app --bind "0.0.0.0:${PORT:-8080}"
