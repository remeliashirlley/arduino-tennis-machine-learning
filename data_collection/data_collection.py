import asyncio
from bleak import BleakClient
import struct  # Ensure struct is imported for unpacking binary data
import pandas as pd

DEVICE_ADDRESS = "78AF8A46-2A2F-C601-03FC-318D28D971EB"  # Replace with your Arduino's BLE address
SENSOR_CHARACTERISTIC_UUID = "12345678-1234-1234-1234-123456789013"  # Replace with the characteristic's UUID

def unpack_sensor_data(data):
    # Data is packed as 6 consecutive floats (aX, aY, aZ, gX, gY, gZ)
    aX, aY, aZ, gX, gY, gZ = struct.unpack('<ffffff', data)
    return aX, aY, aZ, gX, gY, gZ

async def run_ble_client(device_address: str, char_uuid: str):
    async with BleakClient(device_address) as client:
        # Connect to the device
        connected = await client.connect()
        if connected:
            print(f"Connected to {device_address}")

            df = pd.DataFrame(columns=['aX', 'aY', 'aZ', 'gX', 'gY', 'gZ'])

            # Function to handle incoming notifications from the characteristic
            
            def handle_notification(sender, data):
                nonlocal df
                aX, aY, aZ, gX, gY, gZ = unpack_sensor_data(data)
                # print(f"Acceleration Data - X: {aX}, Y: {aY}, Z: {aZ}")
                # print(f"Gyroscope Data - X: {gX}, Y: {gY}, Z: {gZ}")
                print(f'{aX}, {aY}, {aZ}, {gX}, {gY}, {gZ}')
                new_row = {'aX': aX, 'aY': aY, 'aZ': aZ, 'gX': gX, 'gY': gY, 'gZ': gZ}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # Start receiving notifications from the characteristic
            await client.start_notify(char_uuid, handle_notification)
            print("Subscribed to sensor data notifications.")

            # Keep the script running while data is being logged
            await asyncio.sleep(90)  # Run for 30 seconds, adjust as needed

            # Stop receiving notifications
            await client.stop_notify(char_uuid)
            print("Unsubscribed from notifications.")
            print(df)
            df.to_csv('test.csv',index=False)

        else:
            print(f"Failed to connect to {device_address}")

# Replace asyncio.run(...) if you're in an environment that doesn't support it directly
loop = asyncio.get_event_loop()
loop.run_until_complete(run_ble_client(DEVICE_ADDRESS, SENSOR_CHARACTERISTIC_UUID))
