# Multi-Mode Writing Platform Backend

Production backend service built with **FastAPI** and the **Google Antigravity SDK (`google-antigravity`)**. It provides persona-tailored agent orchestration and chunked token streaming for Bloggers, Researchers, and Book Authors.

🌐 **Live Production Deployment**: [https://writingplatformbackend.vercel.app](https://writingplatformbackend.vercel.app)  
🚀 **Interactive Web Playground**: [https://writingplatformbackend.vercel.app/](https://writingplatformbackend.vercel.app/)  
🩺 **Health Endpoint**: [https://writingplatformbackend.vercel.app/health](https://writingplatformbackend.vercel.app/health)  

---

## 🏗️ Architecture & Key Components

```
writing_platform_backend/
├── main.py              # FastAPI app, /generate streaming route & error handling
├── agent_factory.py     # Dynamic LocalAgentConfig factory & persona definitions
├── models.py            # Pydantic schemas (WritingMode, GenerateRequest, HealthResponse)
├── tools.py             # Mock custom tools (academic DB & book bible context)
├── requirements.txt     # Python package requirements
├── test_app.py          # Integration & unit test suite
└── README.md            # Technical documentation
```

### 1. Dynamic Configuration Matrix

| Mode | Temperature | System Instructions Focus | Bound Custom Tools |
| :--- | :--- | :--- | :--- |
| **`blogger`** | `0.7` | SEO optimization, viral hooks, conversational tone, clear CTAs | None |
| **`researcher`** | `0.1` | Zero hallucination, strict factual rigor, empirical grounding | `query_academic_database` |
| **`book_author`**| `0.4` | Narrative continuity, worldbuilding consistency, sensory prose | `fetch_book_bible_context` |

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Service
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📡 API Reference

### Health Check
- **Endpoint**: `GET /health`
- **Response**:
```json
{
  "status": "healthy",
  "service": "Multi-Mode Writing Platform Backend",
  "version": "1.0.0"
}
```

### Content Generation (Streaming)
- **Endpoint**: `POST /generate`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "mode": "blogger",
  "prompt": "Top 5 AI tools transforming productivity in 2026",
  "context_data": "Target audience is tech founders."
}
```
- **Response**: `200 OK` (Stream of tokens chunk-by-chunk with `Transfer-Encoding: chunked`).

---

## 💻 Client Usage Examples

### Using `curl` with Streaming Output
```bash
curl -N -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "researcher",
    "prompt": "Evaluate scaling laws for sparse mixture of experts models.",
    "context_data": "Reference recent 2025-2026 preprints."
  }'
```

### Using Python (`httpx` / `requests`)
```python
import httpx

payload = {
    "mode": "book_author",
    "prompt": "Write the opening scene for Chapter 5 with Kael.",
    "context_data": "Setting: The rainy clocktower of Sector 7."
}

with httpx.stream("POST", "http://localhost:8000/generate", json=payload, timeout=60.0) as response:
    for chunk in response.iter_text():
        print(chunk, end="", flush=True)
```
