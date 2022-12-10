import ctypes
from time import sleep
from threading import Thread

import uvicorn
from loguru import logger
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse


class InTrain:
    def __init__(self):
        self.host = "localhost"
        self.port = 8000
        # ---
        self.app = None
        self.thread = None
        self.socket = None
        self.client_data = None

    def _start_uvicorn(self):
        if self.thread is not None and self.thread.is_alive():
            raise RuntimeError("Already running")
        self.thread = Thread(
            target=self._run_server,
            daemon=True,
        )
        self.thread.start()
        logger.info("Started server at http://{}:{}", self.host, self.port)

    def _run_server(self):
        self._prepare_app()
        uvicorn.run(
            app=self.app,
            host=self.host,
            port=self.port,
            log_config=None,  # TODO: comment out this line when debugging
        )

    def _app_root(self):
        with open("ui.html") as f:
            return HTMLResponse(f.read())

    async def _app_websocket(self, websocket: WebSocket):
        if self.socket is not None:
            logger.info("Closing old socket")
            try:
                await self.socket.close()
            except Exception:
                pass
        self.socket = websocket
        await self.socket.accept()
        logger.info("New socket accepted")

    def _prepare_app(self):
        self.app = FastAPI()
        self.app.get("/")(self._app_root)
        self.app.websocket("/ws")(self._app_websocket)

    def init(self):
        self._start_uvicorn()


if __name__ == "__main__":
    intrain = InTrain()
    intrain.init()
    print("Press Ctrl+C to exit")
    while True:
        sleep(1)
