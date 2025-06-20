import os
import tempfile
import asyncio
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from graph.langgraph_workflow import workflow, TrackerState
from agents import notifier  # ⬅️ Not run inside the graph anymore
from types import SimpleNamespace

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process-jd/")
async def process_jd(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        result = workflow.invoke(TrackerState(file_path=tmp_path))
        os.remove(tmp_path)

        # ✅ Respond to frontend FIRST
        response_data = dict(result)

        # ✅ Trigger notifier in background AFTER returning response
        async def send_notifications():
            try:
                await asyncio.sleep(0)  # give control back to event loop
                print("📬 Triggering email notifications in background...")
                fake_state = SimpleNamespace(**response_data)
                notifier.run(fake_state)
            except Exception as e:
                print("❌ Background mail error:", str(e))

        asyncio.create_task(send_notifications())

        return response_data  # ✅ API responds here immediately

    except Exception as e:
        return {"error": str(e)}
