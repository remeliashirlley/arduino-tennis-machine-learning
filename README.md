## Project Setup

### 1. Setting Up Conda Environment

#### Step 1: Create a New Conda Environment
```
conda create --name myenv python=3.11.8
```

#### Step 2: Activate the Conda Environment
```
conda activate myenv
```

#### Step 3: Install Python Dependecies
```
pip install -r requirements.txt
```

### 2. Upload inference code into Arduino device
Upload the `inference/inference.ino` script

### 3. Get Arduino BLE device address
- To connect to your Arduino BLE device, you'll need to find its device address. Follow these steps:

#### Step 4: Scan for Devices
Run the Python script `scan_devices.py` to scan for BLE devices:
```
python scan_devices.py
```

### 4. Run the Game

#### Step 5: Change device address as found in Step 4
```
cd src
nano BLEDataReceiver.py //declare device address in self.char_uuid 
```

#### Step 6: Launch CustomTkinter GUI
```
python main.py
```
