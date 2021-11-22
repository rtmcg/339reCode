/* Comments are now more sparse, if you are interested in how
   the code works, try making your own comments for it. */


/*================== Pre-Compiler Commands =================*/
  /* Tells compiler what libraries we will be using */
#include <Adafruit_MotorShield.h>
#include <Wire.h>

  /* Gives a name to a constant value before program gets compiles.
   This method uses no program memory space.*/
#define ADDRESS 0x62

/*================== Global Variables ===================*/
unsigned int counter = 0;
char buf[256]; /* Memory space to write strings to */
int mode = 0;
unsigned steps = 1000;
unsigned delays = 20;
unsigned value = 0;

/*  ======= Prepare Motor Shield  ======= */
  /* Create the motor shield object with the default I2C address*/
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
 
  /* Connect a stepper motor with 200 steps per revolution (1.8 degree)
    to motor port #2 (M3 and M4)... This value you will refine from your data!*/
Adafruit_StepperMotor *myMotor = AFMS.getStepper(200, 1);

/*======= setup() and loop() ========*/
void setup() {
  /* Leave this in, in case of compiler bug....*/
  // unsigned getSlope(unsigned history[]) __attribute__((__optimize__("O2")));
  Serial.begin(115200);
  Serial.println("LASER 2017");
  AFMS.begin();         // create with the default frequency 1.6KHz
  //AFMS.begin(1000);   // OR with a different frequency, say 1KHz

  myMotor->setSpeed(10);
  for (int i = 12; i < 14; i++) pinMode(i,OUTPUT);
}

void loop() {
  if (Serial.available()) parse_input();
  if (!mode) return;
  myMotor->step(1, FORWARD, SINGLE);     /* This steps the motor forward one step in SINGLE mode    */
  delay(delays);                         /* Other available modes include DOUBLE (more torque)      */
                                         /* INTERLEAVE (SINGLE followed by DOUBLE) and MICROSTEP    */
  sprintf(buf,"%04d:%04d",counter,analogRead(A0));  /* Send steps and value read to serial (python) */
  Serial.println(buf);
  Serial.flush();
  counter++;
  if (steps == counter) counter = 0;
  if (!counter && (2 == mode)) mode = 0; // waiting to stop
}

/*=========== Function for Using DAC =================*/
void setDAC(int word) {
  char cmd[3];
  word <<= 4;
  cmd[0] = 0x40; //64
  cmd[1] = word >> 8;
  cmd[2] = word & 0xff; //255
  Wire.beginTransmission(ADDRESS);
  if (3 != Wire.write(cmd,3)) {
    Serial.println("FOUL!");
  }
  Wire.endTransmission();
}

/*======== Functions to Interpret Python Commands =========*/
void parse_input() {
  long start = millis();
  for (int i = 0; i < 255; i++) { // fill buffer
    while (!Serial.available()) {
      if ((millis() - start) > 2000) { /* if 2 seconds pass before command */
        Serial.println("Timeout!");    /* give up and                      */
        return;                        /* return to avoid waiting forever  */
      }
    }
    buf[i] = Serial.read();
    if ('\n' == buf[i]) {         
      if (!strncmp("LASER",buf,5)) {
        parse_laser();
        return;
      } else if (!strncmp("STEPS",buf,5)) {
        parse_steps();
        return;
      } else if (!strncmp("DELAY",buf,5)) {
        parse_delays();
        return;
      } else if (!strncmp("START",buf,5)) {
        if (mode) return;
        mode = 1;
        return;
      } else if (!strncmp("STOP",buf,4)) {
        if (!mode) return;
        mode = 2; // set flag to stop at end of loop
        return;
      } else if (!strncmp("ABORT",buf,5)) {
        mode = 0;
        counter = 0;
        return;
      }
    }
  }
}

void parse_laser(void) {
  if (1 != sscanf(buf+6,"%d",&value)) {
    Serial.println("Syntax: LASER <number>\n where <number> is 0..4095");
    return;
  }
  if ((value < 0) || (value > 4095)) {
    Serial.println("LASER range error");
    return;
  }
  setDAC(value);
  return;
}

void parse_steps(void) {
  if (1 != sscanf(buf+6,"%ud",&steps)) {
    Serial.println("Syntax: STEPS <number>");
    return;
  }
  return;
}

void parse_delays(void){
  if (1 != sscanf(buf+6,"%ud",&delays)) {
    Serial.println("Syntax: DELAYS <number>");
  }
  return;
}

