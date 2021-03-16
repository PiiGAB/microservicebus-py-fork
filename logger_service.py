import asyncio
from base_service import BaseService

class Logger(BaseService):
    def __init__(self, id, queue):
        self.debug = True
        super(Logger, self).__init__(id, queue)

    async def _debug(self, message):
       print(f"mSB:[{message.source}] DEGUG: {message.message[0]}")
       if self.debug:
           await self.SubmitAction("msb", "_debug", message.message[0])

    async def Start(self):
        while True:
            await asyncio.sleep(0)
    
    async def StateUpdate(self, message):
        state = message.message[0]
        state_exists = "msb-state" in state["desired"]
        if state_exists:
            if self.debug != state["desired"]["msb-state"]["debug"]:
                self.debug = state["desired"]["msb-state"]["debug"]
                await self.Debug(f"Console debugging is set to {self.debug}")
        