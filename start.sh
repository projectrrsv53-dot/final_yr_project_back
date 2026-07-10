#!/bin/bash

python download_models.py

uvicorn app:app --host 0.0.0.0 --port $PORT