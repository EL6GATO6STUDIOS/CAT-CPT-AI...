from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import asyncio, json
from vllm import LLM, SamplingParams

app = FastAPI()

# Tek ortak key
VALID_KEYS = {"public-key-123"}

llm = LLM(model="meta-llama/Meta-Llama-3-8B-Instruct")
sampling = SamplingParams(temperature=0.7, top_p=0.9, max_tokens=512)

def check_key(x_api_key: str):
    if x_api_key not in VALID_KEYS:
        raise HTTPException(status_code=401, detail="Geçersiz API key")

@app.post("/v1/chat/completions")
async def chat_completions(req: Request):
    body = await req.json()
    x_api_key = req.headers.get("x-api-key")
    check_key(x_api_key)

    messages = body.get("messages", [])
    if not messages:
        raise HTTPException(status_code=400, detail="Mesaj boş olamaz")

    prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

    async def gen():
        outputs = llm.generate([prompt], sampling)
        for out in outputs:
            text = out.outputs[0].text
            for chunk in [text[i:i+80] for i in range(0, len(text), 80)]:
                data = {
                    "id": "cmpl-xyz",
                    "object": "chat.completion.chunk",
                    "choices": [{"delta": {"content": chunk}}],
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
