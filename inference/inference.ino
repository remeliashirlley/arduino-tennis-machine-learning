#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>
#include <TensorFlowLite.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_error_reporter.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/schema/schema_generated.h>
#include <tensorflow/lite/version.h>
#include "DebugLog.h"
#include "model.h"


const char* serviceUUID = "12345678-1234-1234-1234-123456789012";
const char* sensorCharacteristicUUID = "12345678-1234-1234-1234-123456789013";

BLEService sensorService(serviceUUID); 
BLECharacteristic sensorCharacteristic(sensorCharacteristicUUID, BLERead | BLENotify, 24); // 6 floats * 4 bytes each = 24 bytes

const float accelerationThreshold = 4; // Threshold of significant motion in G's
const int numSamples = 119;
int samplesRead = numSamples;

//global variables used for TensorFlow Lite (Micro)
tflite::MicroErrorReporter tflErrorReporter;

// pull in all the TFLM ops, you can remove this line and
// only pull in the TFLM ops you need, if would like to reduce
// the compiled size of the sketch.
tflite::AllOpsResolver tflOpsResolver;

const tflite::Model* tflModel = nullptr;
tflite::MicroInterpreter* tflInterpreter = nullptr;
TfLiteTensor* tflInputTensor = nullptr;
TfLiteTensor* tflOutputTensor = nullptr;

// Create a static memory buffer for TFLM, the size may need to
// be adjusted based on the model you are using
constexpr int tensorArenaSize = 8 * 1024;
byte tensorArena[tensorArenaSize] __attribute__((aligned(16)));

// array to map gesture index to a name
const char* GESTURES[] = {
  "fl",
  "fh",
  "bl",
  "bh"
};

#define NUM_GESTURES (sizeof(GESTURES) / sizeof(GESTURES[0]))


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

  Serial.print("Accelerometer sample rate = ");
  Serial.print(IMU.accelerationSampleRate());
  Serial.println(" Hz");
  Serial.print("Gyroscope sample rate = ");
  Serial.print(IMU.gyroscopeSampleRate());
  Serial.println(" Hz");

  Serial.println();

  tflModel = tflite::GetModel(model);
  if (tflModel->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Model schema mismatch!");
    while (1);
  }

  // Create an interpreter to run the model
  tflInterpreter = new tflite::MicroInterpreter(tflModel, tflOpsResolver, tensorArena, tensorArenaSize, &tflErrorReporter);

  // Allocate memory for the model's input and output tensors
  tflInterpreter->AllocateTensors();

  // Get pointers for the model's input and output tensors
  tflInputTensor = tflInterpreter->input(0);
  tflOutputTensor = tflInterpreter->output(0);
}

void loop() {
  BLEDevice central = BLE.central();

  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());
    
    while (central.connected()) {
        float aX, aY, aZ, gX, gY, gZ;
        if (samplesRead == numSamples && IMU.accelerationAvailable()) {
            IMU.readAcceleration(aX, aY, aZ);
            float aSum = fabs(aX) + fabs(aY) + fabs(aZ);
            if (aSum >= accelerationThreshold) {
            samplesRead = 0; // Reset sample count to start data capture
            }
        }

        if (samplesRead < numSamples && IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
            IMU.readAcceleration(aX, aY, aZ);
            IMU.readGyroscope(gX, gY, gZ);

            tflInputTensor->data.f[samplesRead * 6 + 0] = (aX + 4.0) / 8.0;
            tflInputTensor->data.f[samplesRead * 6 + 1] = (aY + 4.0) / 8.0;
            tflInputTensor->data.f[samplesRead * 6 + 2] = (aZ + 4.0) / 8.0;
            tflInputTensor->data.f[samplesRead * 6 + 3] = (gX + 2000.0) / 4000.0;
            tflInputTensor->data.f[samplesRead * 6 + 4] = (gY + 2000.0) / 4000.0;
            tflInputTensor->data.f[samplesRead * 6 + 5] = (gZ + 2000.0) / 4000.0;
            
            samplesRead++;

            if (samplesRead == numSamples) {
                // Run inferencing
                TfLiteStatus invokeStatus = tflInterpreter->Invoke();
                if (invokeStatus != kTfLiteOk) {
                Serial.println("Invoke failed!");
                while (1);
                return;
                }

                byte tensorData[NUM_GESTURES*4];
                // Loop through the output tensor values from the model
                for (int i = 0; i < NUM_GESTURES; i++) {
                //Serial.print(GESTURES[i]);
                memcpy(tensorData+(i*4), &tflOutputTensor->data.f[i],4);
                Serial.println(tflOutputTensor->data.f[i], 6);
                
                }
                sensorCharacteristic.writeValue(tensorData, NUM_GESTURES * 4);
            }
        }
    }
}
}
