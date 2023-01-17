import sys
import time
import json
import asyncio
import subprocess
import websockets
import websockets.exceptions
import logging.handlers

from nextion import Display, Tags
from servo import Servo

local_server_address = "192.168.25.4"
server_address = "159.65.118.24"
server_http_port = "5000"
server_websocket_port = "8765"
serial_port_name = "/dev/ttyUSB0"
servo_pin = 17

# Custom logger
log_formatter = logging.Formatter("%(asctime)-15s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
log_stream_handler = logging.StreamHandler(stream=sys.stdout)
log_stream_handler.setFormatter(log_formatter)
log = logging.getLogger("websocket_server")
log.setLevel(logging.DEBUG)
log.addHandler(log_stream_handler)

display = Display(serial_port_name)
servo = Servo(servo_pin)


def get_hw_id():
    mac = subprocess.check_output(["cat", "/sys/class/net/wlan0/address"])
    hw_id = str(mac.decode()).replace(":", "").replace("\n", "")
    return hw_id


sell_url = f"http://{server_address}:{server_http_port}/sell?hw_id={get_hw_id()}"
purchase_url = f"http://{server_address}:{server_http_port}/purchase?hw_id={get_hw_id()}"


async def keep_connected():
    async with websockets.connect(f"ws://{server_address}:{server_websocket_port}") as websocket:
        try:
            display.update_page(Tags.OpeningPage.Tag)
            display.update_text(Tags.OpeningPage.MessageTag, "Connecting...")
            event = {"type": "connect", "hw_id": get_hw_id()}

            await websocket.send(json.dumps(event))
            time.sleep(3)
            display.update_page(Tags.RegisterPage.Tag)
            display.update_text(Tags.PurchasePage.CodeTag, sell_url)

            while True:
                message = await websocket.recv()
                event = json.loads(message)
                log.debug(event)

                if event["type"] == "response":
                    log.info(event.get("message"))
                elif event["type"] == "command":
                    command = event["command"]
                    item_name = event["item"]["name"]
                    item_price = event["item"]["price"]
                    if command == "lock":
                        display.update_page(Tags.PurchasePage.Tag)
                        display.update_text(Tags.PurchasePage.NameTag, item_name)
                        display.update_text(Tags.PurchasePage.PriceTag, item_price + "TL")
                        display.update_text(Tags.PurchasePage.CodeTag, purchase_url)
                        servo.lock()
                    elif command == "unlock":
                        servo.unlock()
                        display.update_page(Tags.RegisterPage.Tag)
                        display.update_text(Tags.PurchasePage.CodeTag, sell_url)
                else:
                    log.debug("invalid event")
        except websockets.exceptions.ConnectionClosedOK:
            log.info("connection closed")
        except Exception as e:
            log.exception(e)


if __name__ == "__main__":
    try:
        asyncio.run(keep_connected())
    except Exception as exception:
        log.exception(exception)
