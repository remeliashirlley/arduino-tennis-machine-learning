#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

const char* serviceUUID = "12345678-1234-1234-1234-123456789012";
const char* sensorCharacteristicUUID = "12345678-1234-1234-1234-123456789013";

BLEService sensorService(serviceUUID); 
BLECharacteristic sensorCharacteristic(sensorCharacteristicUUID, BLERead | BLENotify, 24); // 6 floats * 4 bytes each = 24 bytes

const float accelerationThreshold = 4; // Threshold of significant motion in G's
const int numSamples = 119;
int samplesRead = numSamples;

void setup() {
  Serial.begin(9600);
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  if (!BLE.begin()) {
    Serial.println("Starting BLE failed!");
    while (1);
  }

  BLE.setLocalName("Arduino Sensors");
  BLE.setAdvertisedService(sensorService);
  sensorService.addCharacteristic(sensorCharacteristic);
  BLE.addService(sensorService);
  BLE.advertise();

  Serial.println("BLE Sensor Service is now active. Waiting for connections...");
}

void loop() {
  BLEDevice central = BLE.central();

  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());
    
    while (central.connected()) {
      float aX, aY, aZ, gX, gY, gZ;
      // wait for significant motion
      if (samplesRead == numSamples && IMU.accelerationAvailable()) {
        // Read acceleration to check for significant motion
        IMU.readAcceleration(aX, aY, aZ);
        float aSum = fabs(aX) + fabs(aY) + fabs(aZ);
        if (aSum >= accelerationThreshold) {
          samplesRead = 0; // Reset sample count to start data capture
        }
      }

      // Capture and send data if significant motion was detected
      if (samplesRead < numSamples && IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
        IMU.readAcceleration(aX, aY, aZ);
        IMU.readGyroscope(gX, gY, gZ);
        samplesRead++;

        byte sensorData[24]; // 6 floats * 4 bytes each = 24 bytes
        memcpy(sensorData, &aX, 4);
        memcpy(sensorData + 4, &aY, 4);
        memcpy(sensorData + 8, &aZ, 4);
        memcpy(sensorData + 12, &gX, 4);
        memcpy(sensorData + 16, &gY, 4);
        memcpy(sensorData + 20, &gZ, 4);

        sensorCharacteristic.writeValue(sensorData, 24); // Send data over BLE
      }
    }
    Serial.println("Disconnected from central.");
  }
}
