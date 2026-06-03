# Mini Hackathon VinUni

## Project Structure

- `src/agents`: LangGraph agent graph, state, nodes, and tools
- `src/api`: FastAPI routes
- `src/models`: Pydantic schemas
- `src/services`: business logic
- `src/static`: existing frontend UI
- `tests`: pytest suite
- `scripts`: AI usage logging hooks
- `docs`: guidebook and architecture notes
- `eval`: evaluation artifacts
- `presentation`: demo day slides

## Run

```bash
python -m pip install -r requirements.txt
uvicorn src.main:app --reload
```
