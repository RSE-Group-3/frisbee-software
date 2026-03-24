#include <Servo.h>
#include <AccelStepper.h>

// Launcher motor
Servo myESC;
const int ESC_PIN = 21;  
const int RUN_TIME = 3000;
const int STOP_SPEED = 1000;

// Stepper motor
const int dirPin = 3;
const int stepPin = 2;
#define motorInterfaceType 1
AccelStepper myStepper(motorInterfaceType, stepPin, dirPin);

void setup() {
  Serial.begin(9600); 
  myESC.attach(ESC_PIN);

  myESC.writeMicroseconds(STOP_SPEED);
  delay(10000);
  Serial.println("Launcher READY");

  // Stepper motor
  myStepper.setMaxSpeed(1000);
  myStepper.setAcceleration(500);
  myStepper.moveTo(200);
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.startsWith("LAUNCHER:")) {
      int firstSpace = input.indexOf(' ');
      int secondSpace = input.indexOf(' ', firstSpace+1);

      if (firstSpace != -1 && secondSpace != -1) {
        String command = input.substring(firstSpace+1, secondSpace);
        String distStr = input.substring(secondSpace+1);
        int distVal = distStr.toInt();

        int speedVal = distanceToRPM(distVal);
        executeLaunch(speedVal);

      } else{
        Serial.println("Error: Format mismatch");
      }
    }

    if (input.startsWith("COLLECTOR:")){
      int firstSpace = input.indexOf(' ');
      int secondSpace = input.indexOf(' ', firstSpace+1);

      if (firstSpace != -1 && secondSpace != -1){
        // run stepper motor
        if (myStepper.distanceToGo() == 0) {
          myStepper.moveTo(-myStepper.currentPosition());
        }
        Serial.println("Stepper moving...");
        while (myStepper.distanceToGo() != 0) {
          myStepper.run(); 
        }
        Serial.println("Stepper arrived.");
      }
    }
  }
}

int distanceToRPM(int val){
  float trans = 250.0;
  float voltage = 14.8;
  float maxRPM = voltage * trans;

  float targetRPM = val;
  float throttle = targetRPM / maxRPM;
  int speed = (int)(1000.0 * throttle) + 1000;
  Serial.println(speed);
  return speed;
}

void executeLaunch(int val) {
  if (val >= 1050 && val <= 2000) {
    Serial.print("ACTION: Launching at ");
    Serial.println(val);

    myESC.writeMicroseconds(val);
    delay(RUN_TIME);
    myESC.writeMicroseconds(STOP_SPEED);

    Serial.println("STATUS: Cycle Finished");
  } else {
    Serial.println("ERROR: Speed Out of Bounds");
  }
}