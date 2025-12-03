#include <Arduino.h>
#include <ESP32Servo.h>
 
const int trigPin = 22;
const int echoPin = 23;
Servo myServo;
const int servoPin = 16;
long duration;
int distance;
 
void setup() {
  Serial.begin(115200);
 
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
 
  myServo.attach(servoPin);
  myServo.write(180); //Servo auf 180 Grad setzen
}
 
void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
 
  duration = pulseIn(echoPin, HIGH, 30000);
  distance = duration * 0.034 / 2;
 
  Serial.print("Sensorwert (Dauer): ");
  Serial.print(duration);
  Serial.print(" µs   |   ");
 
  Serial.print("Entfernung: ");
  Serial.print(distance);
  Serial.println(" cm");
 
  if (distance > 0 && distance < 15) {
    myServo.write(0);
    delay(500);
  } else {
    myServo.write(180);
  }
 
  delay(200);
}