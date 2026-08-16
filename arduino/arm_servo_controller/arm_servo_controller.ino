#include <Servo.h>

const byte SERVO_COUNT = 5;
const byte SERVO_PINS[SERVO_COUNT] = {3, 5, 6, 9, 10};

Servo servos[SERVO_COUNT];
char inputBuffer[64];
byte inputLength = 0;

bool parseAndMove(char *line) {
  int angles[SERVO_COUNT];
  byte count = 0;
  char *savePointer;
  char *token = strtok_r(line, ",", &savePointer);

  while (token != NULL && count < SERVO_COUNT) {
    char *endPointer;
    long value = strtol(token, &endPointer, 10);
    if (*endPointer != '\0') {
      return false;
    }
    angles[count++] = constrain(value, 0, 180);
    token = strtok_r(NULL, ",", &savePointer);
  }

  if (count != SERVO_COUNT || token != NULL) {
    return false;
  }

  for (byte index = 0; index < SERVO_COUNT; index++) {
    servos[index].write(angles[index]);
  }
  return true;
}

void setup() {
  Serial.begin(115200);
  for (byte index = 0; index < SERVO_COUNT; index++) {
    servos[index].attach(SERVO_PINS[index]);
    servos[index].write(90);
  }
  delay(500);
  Serial.println("READY");
}

void loop() {
  while (Serial.available() > 0) {
    char incoming = Serial.read();

    if (incoming == '\r') {
      continue;
    }
    if (incoming == '\n') {
      inputBuffer[inputLength] = '\0';
      if (parseAndMove(inputBuffer)) {
        Serial.println("OK");
      } else {
        Serial.println("ERROR");
      }
      inputLength = 0;
      continue;
    }

    if (inputLength < sizeof(inputBuffer) - 1) {
      inputBuffer[inputLength++] = incoming;
    } else {
      inputLength = 0;
      Serial.println("ERROR");
    }
  }
}
