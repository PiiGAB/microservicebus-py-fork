import asyncio, logging
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import MethodResponse
from base_service import BaseService

class AzureIoT(BaseService):
    def __init__(self, id, queue, provider_info):
        logger = logging.getLogger('azure.iot.device')
        logger.setLevel(logging.WARNING)
        self.device_client = IoTHubDeviceClient.create_from_connection_string(provider_info["connectionString"])
        self.device_client.on_method_request_received = self.method_request_handler
        self.device_client.on_twin_desired_properties_patch_received = self.twin_patch_handler
        self.twin = None
        super(AzureIoT, self).__init__(id, queue)

    async def Start(self):
        await self.device_client.connect()
        self.twin = await self.device_client.get_twin()

        if(self.twin["desired"]["msb-state"]["enabled"] == False):
            await self.StopCustomServices()
        
        await self.Debug("Com is started")
        while True:
            await asyncio.sleep(1)

    async def Process(self, message):
        #await self.device_client.send_message(message.message[0])
        await self.Debug("Message sent to IoT Hub")
    
    async def twin_patch_handler(self, patch):
        if(self.twin["desired"]["msb-state"]["enabled"] != patch["msb-state"]["enabled"]):
            if(patch["msb-state"]["enabled"] == False):
                await self.StopCustomServices()
            else:
                await self.StartCustomServices()

        await self.SubmitAction("*", "StateUpdate", patch)
        self.twin = await self.device_client.get_twin()

    async def method_request_handler(self, method_request):
        await self.Debug(f"Inbound call: {method_request.name}")
        # Determine how to respond to the method request based on the method name
        if method_request.name == "stop":
            await self.StopCustomServices()
            payload = {"result":"All services stopped"}
            status = 200 
        elif method_request.name == "start":
            await self.StartCustomServices()
            payload = {"result":"All services started"}
            status = 200 
        else:
            payload = {"result": False, "data": "unknown method"}  # set response payload
            status = 400  # set return status code
            print("executed unknown method: " + method_request.name)

        # Send the response
        method_response = MethodResponse.create_from_method_request(method_request, status, payload)
        await self.device_client.send_method_response(method_response)
