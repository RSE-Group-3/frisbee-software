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

// for parsing commands
struct Command {
  String type = ""; // LAUNCHER | COLLECTOR | WHEELS | STOP
  String action = "";    // e.g. launch
  int value1 = 0;        // e.g. distance or left wheel velocity
  int value2 = 0;        // e.g. right wheel velocity
};

/**
 * input:
 *   LAUNCHER launch <value>
 *   COLLECTOR <action> 
 *   WHEELS speed <left> <right>
 *   STOP
 * output:
 *   OK: info
 *   STOP: info
 */
Command parseCommand(String input) {
  Command cmd;
  int firstSpace = input.indexOf(' ');
  int secondSpace = input.indexOf(' ', firstSpace + 1);
  int thirdSpace = input.indexOf(' ', secondSpace + 1);

  if (firstSpace != -1) {
    cmd.type = input.substring(0, firstSpace);
    if (cmd.type.endsWith(":")) {
        cmd.type = cmd.type.substring(0, cmd.type.length() - 1);
    }
  } else {
    cmd.type = input;
    if (cmd.type.endsWith(":")) {
        cmd.type = cmd.type.substring(0, cmd.type.length() - 1);
    }
    return cmd;
  }

  if (secondSpace != -1) {
    cmd.action = input.substring(firstSpace + 1, secondSpace);
  } else {
    cmd.action = input.substring(firstSpace + 1);
    return cmd;
  }

  if (thirdSpace != -1) {
    cmd.value1 = input.substring(secondSpace + 1, thirdSpace).toInt();
    cmd.value2 = input.substring(thirdSpace + 1).toInt();
  } else {
    cmd.value1 = input.substring(secondSpace + 1).toInt();
  }

  return cmd;
}

void executeCommand(Command cmd) {
  if (cmd.type == "LAUNCHER") {
    if (cmd.action == "launch") {
      executeLaunch(cmd.value1);
    } else {
      Serial.println("FAIL: Unknown launcher action");
    }

  } else if (cmd.type == "COLLECTOR") {
    if (cmd.action == "test") {
      executeCollectorTest();
    } else if (cmd.action == "reset") {
      executeCollectorReset();
    } else { // TODO: add other actions
      Serial.println("FAIL: Unknown collector action");
    }

  } else if (cmd.type == "WHEELS") {
    if (cmd.action == "speed") {
      executeWheelVelocity(cmd.value1, cmd.value2); 
    } else {
      Serial.println("FAIL: Unknown wheel action");
    }

  } else if (cmd.type == "STOP") {
    executeStop();

  } else {
    Serial.println("FAIL: Unknown command");
  }
}

//----------------------------------------------------------------

int rpmToESC(int val) {  
  float trans = 250.0;
  float voltage = 14.8;
  float maxRPM = voltage * trans;

  float targetRPM = val;
  float throttle = targetRPM / maxRPM;
  int speed = (int)(1000.0 * throttle) + 1000;
//   Serial.println(speed);
  return speed;
}

// LAUNCHER launch <val>
void executeLaunch(int val) {
  // input val is currently rpm. TODO: distance conversion?
  int esc_val = rpmToESC(val);

  if (!(esc_val >= 1050 && esc_val <= 2000)) {
    Serial.println("FAIL: Launch speed out of bounds");
    return;
  }

  Serial.print("ACTION: Launching at ");
  Serial.println(esc_val);

  myESC.writeMicroseconds(esc_val);
  delay(RUN_TIME);
  myESC.writeMicroseconds(STOP_SPEED);

  Serial.println("OK: Launch cycle finished");
}

// COLLECTOR test
void executeCollectorTest() {
  if (myStepper.distanceToGo() == 0) {
      myStepper.moveTo(-myStepper.currentPosition());
  }
  Serial.println("Stepper moving...");
  while (myStepper.distanceToGo() != 0) {
      myStepper.run(); 
  }
  Serial.println("Stepper arrived.");

  Serial.println("OK: Stepper test finished");
}

// COLLECTOR reset
void executeCollectorReset() {
  // TODO: move collector to default position
  Serial.println("OK: Collector successfully reset position");
}

// WHEELS vl_vr <left_vel> <right_vel>
void executeWheelVelocity(int left_vel, int right_vel) {
  // TODO: set wheel velocities
  ;
  // don't print "OK: ..." (not needed for wheels)
}

// STOP
void executeStop() {
  // TODO: stop all motors safely
  Serial.println("OK: Skipped stopping all motors");
}

//----------------------------------------------------------------

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
    Command cmd = parseCommand(input);
    executeCommand(cmd);
  }
}