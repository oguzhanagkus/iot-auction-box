import sys
import json
import asyncio
import websockets
import logging.handlers

# Custom logger
log_formatter = logging.Formatter("%(asctime)-15s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
log_stream_handler = logging.StreamHandler(stream=sys.stdout)
log_stream_handler.setFormatter(log_formatter)
log = logging.getLogger("websocket_server")
log.setLevel(logging.DEBUG)
log.addHandler(log_stream_handler)

# Connected devices with their hw_id and websocket object
connected_devices = {}


# Keep devices connected
async def keep_connected(websocket, event):
    hw_id = event.get("hw_id")
    if hw_id:
        connected_devices[hw_id] = websocket
        log.debug(connected_devices)
        try:
            async for message in websocket:
                event = json.loads(message)
                log.debug(event)
        except Exception as e:
            log.exception(e)
            data = {"type": "response", "message": "exception occurred", "status": False}
            await websocket.send(json.dumps(data))
        finally:
            del connected_devices[hw_id]
    else:
        data = {"type": "response", "message": "no hw_id supplied", "status": False}
        await websocket.send(json.dumps(data))


# Send commands to devices from web-server
async def send_command(websocket, event):
    hw_id = event.get("hw_id")
    if hw_id:
        try:
            connection = connected_devices.get(hw_id)
            if connection:
                await connection.send(json.dumps(event))
            else:
                data = {"type": "response", "message": "no connection with device", "status": False}
                await websocket.send(json.dumps(data))
        except Exception as e:
            log.exception(e)
            data = {"type": "response", "message": "exception occurred", "status": False}
            await websocket.send(json.dumps(data))
    else:
        data = {"type": "response", "message": "no hw_id/command supplied", "status": False}
        await websocket.send(json.dumps(data))


# Wrapper function
async def handler(websocket):
    try:
        message = await websocket.recv()
        event = json.loads(message)
        log.debug(event)

        data = {"type": "response", "message": "connected to websocket-server"}
        await websocket.send(json.dumps(data))

        if event["type"] == "connect":
            await keep_connected(websocket, event)
        elif event["type"] == "command":
            await send_command(websocket, event)
        else:
            data = {"type": "response", "message": "invalid event", "status": False}
            await websocket.send(json.dumps(data))
    except Exception as e:
        log.exception(e)
        data = {"type": "response", "message": "exception occurred", "status": False}
        await websocket.send(json.dumps(data))


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exception:
        log.exception(exception)
