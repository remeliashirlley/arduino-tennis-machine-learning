import asyncio
from bleak import BleakClient
import struct
import queue
from threading import Thread
import numpy as np

class BLEDataReceiverThread(Thread):
    """
    1. Receive inference data from Arduino in the format <ffff> in the sequence of Forehand Low, Forehand High, Backhand Low, Backhand High
    2. Extends the Thread class to implement threading for BLE receive fn
    3. Modifies queue by putting inference result into mutable queue object

    Args:
        queue (queue.Queue): queue to put the processed sensor data
        sleep_time (int): time interval to wait between data reception

    Return:
        None
    """

    def __init__(self, queue:queue.Queue, sleep_time:int):
        super().__init__()
        self.device_address = "78AF8A46-2A2F-C601-03FC-318D28D971EB"
        self.char_uuid = "12345678-1234-1234-1234-123456789013"
        self.queue = queue
        self.sleep_time=sleep_time
        self.subscribe=None

    async def unpack_sensor_data(self, data):
        fl,fh,bl,bh = struct.unpack('<ffff', data)
        return fl,fh,bl,bh 

    async def handle_notification(self, sender, data):
        fl,fh,bl,bh = await self.unpack_sensor_data(data)
        print(fl,fh,bl,bh )
        result=np.argmax(np.array([fl,fh,bl,bh ]))
        self.queue.put(result)

    def run(self):
        async def ble_task():
            async with BleakClient(self.device_address) as client:
                connected = await client.connect()
                if connected:
                    print(f"Connected to {self.device_address}")
                    await client.start_notify(self.char_uuid, self.handle_notification)
                    self.subscribe=True
                    print("Subscribed to sensor data notifications.")
                    await asyncio.sleep(self.sleep_time)
                    await client.stop_notify(self.char_uuid)
                    self.subscribe=False
                    print("Unsubscribed from notifications.")
                else:
                    print(f"Failed to connect to {self.device_address}")

        asyncio.run(ble_task())