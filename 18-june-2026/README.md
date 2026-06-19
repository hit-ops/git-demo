# 18-june-2026 — FastAPI example

This folder contains a small FastAPI example with an in-memory store.

Run the app (from this folder, with your virtualenv activated):

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Endpoints:

- `POST /items/` — create item
- `GET /items/` — list items
- `GET /items/{id}` — get item
- `PUT /items/{id}` — update item
- `DELETE /items/{id}` — delete item
