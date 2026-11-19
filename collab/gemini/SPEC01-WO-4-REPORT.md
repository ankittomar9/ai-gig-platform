# [SPEC01-WO-4] Fix Docker Build & Compose (F4 Remediation)
- **Author:** Gemini / Antigravity
- **Date:** 2026-11-20
- **Base Commit:** `f057154`
- **Branch:** `docker/fresh-clone-build-fix`
- **Verdict:** EXECUTED

---

## 1. Summary of Changes
- **Removed Broken `COPY data/ ./data/`:** In `Dockerfile`, removed the line copying `data/`. The directory `data/` is gitignored and created dynamically at runtime by `app/config.py` (`DATA_DIR.mkdir(exist_ok=True)`). Persistence is managed via Docker volume mount `./data:/app/data`.
- **Made `.env` Optional in `docker-compose.yml`:** Updated compose file from hard requirement `env_file: - .env` to:
  ```yaml
  env_file:
    - path: .env
      required: false
  ```
- **Added Health Endpoint & Healthcheck Alignment:** Added `GET /health` (`{"status": "ok", "app": "ai-gig-platform"}`) in `app/main.py` and updated container health checks in `Dockerfile` and `docker-compose.yml` to query `http://localhost:8000/health`.

---

## 2. Acceptance Test Evidence (Verbatim Receipts)

Executed in a fresh isolated clone in temporary directory with **no `data/`** directory and **no `.env`** file.

Command executed:
```powershell
$testDir = Join-Path $env:TEMP "aigig-fresh-test"
git clone -b docker/fresh-clone-build-fix D:\ai-gig-platform $testDir
cd $testDir

Write-Host "Verifying no data/ directory exists:" (Test-Path "data")
Write-Host "Verifying no .env file exists:" (Test-Path ".env")

docker build -t aigig-fresh-success .
docker run -d -p 8008:8000 --name aigig_fresh_test aigig-fresh-success
Start-Sleep -Seconds 4

$resp = curl.exe -s http://localhost:8008/health
Write-Host "Healthcheck Response:" $resp

docker rm -f aigig_fresh_test
```

Raw Command Output:
```text
Cloning into 'C:\Users\tomar\AppData\Local\Temp\aigig-fresh-test'...
done.
Verifying no data/ directory exists: False
Verifying no .env file exists: False
#0 building with "desktop-linux" instance using docker driver
#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 873B 0.0s done
#1 DONE 0.0s
#2 [internal] load metadata for docker.io/library/python:3.12-slim
#2 DONE 0.4s
#3 [internal] load .dockerignore
#3 transferring context: 150B done
#3 DONE 0.0s
#4 [1/6] FROM docker.io/library/python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
#4 DONE 0.0s
#5 [internal] load build context
#5 transferring context: 209.20kB 0.1s done
#5 DONE 0.1s
#6 [2/6] WORKDIR /app
#6 CACHED
#7 [3/6] RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
#7 CACHED
#8 [4/6] COPY requirements.txt .
#8 DONE 0.1s
#9 [5/6] RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
#9 DONE 11.1s
#10 [6/6] COPY app/ ./app/
#10 DONE 0.1s
#11 exporting to image
#11 naming to docker.io/library/aigig-fresh-success:latest done
#11 unpacking to docker.io/library/aigig-fresh-success:latest 1.0s done
#11 DONE 4.6s

52efa9af97d9f0f0a3dd254154cc58c588f6e12975a189e79fdc80d7b6078899
Healthcheck Response: {"status":"ok","app":"ai-gig-platform"}
aigig_fresh_test
```

---

## 3. Honest-Judge Verification Pair
- **Deliberate Failure Test (Original Broken State):**
  - Attempting build with `COPY data/ ./data/` when `data/` is missing:
  - Error: `failed to calculate checksum ... "/data": not found` (Reproduced and verified).
- **Known-Good Assertion (Remediated State):**
  - Fresh clone build with `COPY data/` removed succeeds with exit code 0.
  - Container runs and `GET /health` returns HTTP 200 with `{"status":"ok","app":"ai-gig-platform"}`. ✅ PASS
