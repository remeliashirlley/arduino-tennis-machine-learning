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
nano BLEDataReceiver.py
```
declare device address in self.char_uuid 

#### Step 6: Launch CustomTkinter GUI
```
python main.py
```

</br></br>

## File Structure
```
.
├── README.md
├── data                    //folder with collected data
│   ├── backhand_high.csv
│   ├── backhand_low.csv
│   ├── forehand_high.csv
│   └── forehand_low.csv
│   ├── ....
├── data_collection         //scripts to collect new data
│   ├── capture
│   │   └── capture.ino     //arduino script to send sensor data through BLE
│   └── data_collection.py  //python script to read sensor data from BLE
├── inference               //folder for inference
│   ├── DebugLog.h
│   ├── inference.ino       //arduino script to run inference
│   └── model.h
├── model                   //TF model training
│   ├── model.cc
│   ├── model.h
│   ├── model.ipynb
│   ├── model.tflite
│   ├── model_best.keras
│   ├── model_final.keras
│   └── model_quantized.tflite
├── plots
│   ├── ....
├── scan_devices.py         //script to get Arduino BLE device address
├── src                     //source folder to run game
│   ├── BLEDataReceiver.py
│   ├── app.py
│   ├── assets
│   │   ├── ....
│   └── main.py             //main script to run game
└── ....
```
