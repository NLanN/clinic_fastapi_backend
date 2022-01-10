#!/bin/bash

worker=${WORKER:-1}
port=${PORT:-8080}

# Migrate database
sleep 2
alembic upgrade head

#run 
uvicorn --host 0.0.0.0 --port ${port} --workers ${worker}  main:app 