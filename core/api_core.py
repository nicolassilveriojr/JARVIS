import os
import sys
import threading
import time
import json
from datetime import datetime

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError:
    FastAPI = None

class JarvisCoreAPI:
    def __init__(self, jarvis_instance):
        self.jarvis = jarvis_instance
        self.app = None
        if FastAPI:
            self.app = FastAPI(title="JARVIS Core API (Mark III)")
            self._setup_routes()

    def _setup_routes(self):
        @self.app.get("/")
        async def root():
            return {
                "status": "online",
                "version": "3.3.0",
                "entity": "JARVIS Mark III",
                "timestamp": datetime.now().isoformat()
            }

        @self.app.post("/query")
        async def query(request: Request):
            data = await request.json()
            prompt = data.get("prompt", "")
            if not prompt:
                return JSONResponse(status_code=400, content={"error": "Prompt is required"})
            
            try:
                historico = self.jarvis.memory.get_recent(limit=5)
                response = self.jarvis.brain.responder(prompt, historico=historico)
            except Exception as e:
                response = f"[STARK PROXY ACTIVE] Sir, o modelo principal atingiu o limite. {str(e)}"
            
            if "[[" in response:
                cmd_res = self.jarvis.commands.processar(response)
                return {"response": response, "command_result": cmd_res, "status": "processed"}
            
            return {"response": response, "status": "success"}

        @self.app.get("/status")
        async def status():
            import psutil
            return {
                "cpu": psutil.cpu_percent(),
                "ram": psutil.virtual_memory().percent,
                "uptime": time.time() - psutil.boot_time(),
                "mode": self.jarvis.brain.api_mode
            }

    def run(self, host="0.0.0.0", port=8008):
        if not self.app:
            return None
        def _start():
            uvicorn.run(self.app, host=host, port=port, log_level="error")
        t = threading.Thread(target=_start, daemon=True)
        t.start()
        return f"http://{host}:{port}"
