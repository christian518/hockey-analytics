@echo off
cd C:\hockey-analytics
docker-compose up -d
timeout /t 20 /nobreak
start http://localhost:3000
start http://localhost:3001