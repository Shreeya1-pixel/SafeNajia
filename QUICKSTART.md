# SafeNaija Quickstart

```bash
# Terminal 1 — API
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH="$(pwd)"
uvicorn safeo_backend.main:app --host 127.0.0.1 --port 8001 --reload

# Terminal 2 — UI
cd frontend/website
npm install
npm run dev
```

- UI: http://localhost:5174  
- API: http://127.0.0.1:8001/nigeria/features  
- Swagger: http://127.0.0.1:8001/docs  

### Smoke test

```bash
curl -s -X POST http://127.0.0.1:8001/nigeria/scan/message \
  -H 'Content-Type: application/json' \
  -d '{"text":"Abeg send the OTP sharp sharp","channel":"whatsapp"}' | python3 -m json.tool
```

Expect `"decision": "BLOCK"`.
