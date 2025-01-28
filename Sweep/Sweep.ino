#include <Servo.h>

// Define the servo objects
Servo baseMotor;   // servo for spinning base
Servo headMotor;   // servo for tiltin the head, keep it smooth
Servo armMotor;    // servo for movin the arm, reach 4 da stars

// Define the LED pin
const int ledPin = 3; // da blink blink

void setup() {
  Serial.begin(9600);         
  baseMotor.attach(9);        // base @ 9
  headMotor.attach(11);       // head @ 11
  armMotor.attach(10);        // arm @ 10
  pinMode(ledPin, OUTPUT);    // set da LED pin to output mode, obv
  Serial.println("Arduino Ready"); // all set
}

void loop() {
  // check if command slid into da serial port
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');  // grab da command until \n
    Serial.println("Received Command: " + command); 

    // Parse da command: L (light), B (base), H (head), A (arm)
    if (command.startsWith("L")) {
      int brightness = command.substring(1).toInt();  
      if (brightness >= 0 && brightness <= 255) {
        analogWrite(ledPin, brightness);  // adjust da brightness
        Serial.println("Set Light Brightness to: " + String(brightness));  // flex da brightness
      }
    } else if (command.startsWith("B")) {
      int baseAngle = command.substring(1).toInt();  
      if (baseAngle >= 0 && baseAngle <= 180) {
        baseMotor.write(baseAngle);  // spin spin da base
        Serial.println("Set Base Motor to: " + String(baseAngle));  // brag about da base angle
      }
    } else if (command.startsWith("H")) {
      int headAngle = command.substring(1).toInt();
      if (headAngle >= 0 && headAngle <= 180) {
        headMotor.write(headAngle);  // tilt it, smooth af
        Serial.println("Set Head Motor to: " + String(headAngle));  // show off da tilt
      }
    } else if (command.startsWith("A")) {
      int armAngle = command.substring(1).toInt();
      if (armAngle >= 0 && armAngle <= 180) {
        armMotor.write(armAngle);  // arm stretch vibes
        Serial.println("Set Arm Motor to: " + String(armAngle));  // tell 'em about da arm
      }
    } else {
      Serial.println("Error: Unknown Command");  // uhhh... wat dis cmd tho?
    }
  }
}