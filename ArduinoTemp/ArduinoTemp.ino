/* 
 * Servo Sketch 
 *   Last edit 13h30 March 8, 2016
 *   Reviewed and commented Summer 2018
 */

 
/*=========== Preprocessor Macro Definitions ===========*/
void register_variable(double *address, const char *name, int record, const char *units);
#define RECORD(X,UNITS) register_variable(&X,#X, 1, UNITS)
#define INITIALIZE(X,VALUE,UNITS) X = VALUE; register_variable(&X,#X, 0, UNITS)

// A0 is default pin for thermocouple readings
int fanPin = 13;
//int blockPin = 11;

/*============== Space for Custom Variables ============
 * These are the global variables used in the controller.     
 * To create your own variables, first declare a double here. 
 */

double dt;
double temperature;
double e_temperature;
double error;
double prevError;
double Tset;
double band;
double out;

void userSetup() {
  /* This function is called at program startup.  There are two useful things to do here:  
   *  
   * RECORD(variableName,units)
   *      This will register a variable to be sent back to the computer at each time step.
   *      The variable should be a globaly defined double precision variable (see temperature above).
   *      The 'units' argument is a string used for labels.
   * INITIALIZE(variableName,value,units)
   *      This will register a variable which can be set from the computer.
   *      The variable should be a globably defined double.
   *      The value is used as the default value.
   *      The 'units' argument is a string used for labels.
   */   
  RECORD(temperature,"K");
  RECORD(e_temperature,"K");
  RECORD(error,"");
  RECORD(out,"DAC units");
  INITIALIZE(dt,0.1,"s");
  INITIALIZE(Tset,350,"K");
  INITIALIZE(band,5,"K");

}
void userAction() {
  /*
   *  This function will be called each time step (dt).
   *  Here is where you will be implementing your control algorithms.
   */  
  long sum = 0, sumsq = 0;
  int value;
  const int N = 16;                 // number of samples measured per time step */
  for (int i = 0; i < N; i++) {     // record N samples */
    value =  analogRead(A0);
    sum += value;                   // used to calculate mean */
    sumsq += value*(long)value;     // used to calulate variance, need to type cast to long because int is 16 bit */
  }
  
  /*  Below here and within userAction(), all the various variables of interest
   *  should be manipulated to be sent to the controller for display. 
   */
  double mu, sigma;
  mu = sum / (double) N;
  sigma = sqrt((sumsq - sum*mu)/N); // expansion of definition of variance */
  
  const double ADCslope = 4.888e-3; // 4.888mV / bit */
  const double ADCoffset = 1.02e-3; // 1.02 mV */
  double vThermo, eVThermo;
  vThermo = ADCslope * mu + ADCoffset; // convert means in ADC units to voltages */
  eVThermo = ADCslope * sigma;
  
  const double thermoSlope = 100; // Kelvin per Volt */
  const double thermoOffset = 273; // K */
  temperature = thermoSlope * vThermo + thermoOffset;
  e_temperature = eVThermo * vThermo;
  prevError = error;
  error = (temperature - Tset);// /  band;
  
  double Ton = Tset - band / 2;
  double Toff = Tset + band / 2;

  if ((out > 0) && (temperature > Toff)) {
    out = 0;
  } else if ((out == 0) && (temperature < Ton)) {
    out = 255;
  }
  int dacVal = out;
/*  
 * Serial.print("DEBUG\tdacVal = ");
 * Serial.print(dacVal);
 * Serial.print("\n");
 */
  analogWrite(11, dacVal);  

}

/*======================*/
void userStart() {// This function is called when the algorithm is started
  out = 0;
}
void userStop() {// This function is called when the algorithm is stopped
 analogWrite(11, 0); /* turn off  heating block*/
}
/*======================*/

/**********************************************
 * Don't worry about the code below this line *
 * Unless you are curious, but be forewarned  *
 * there is a lot of detail below.            *
 **********************************************/

//storage variables
int counter = 0, oc = 0; //Indexes for void loop() and the ISR(), respectively
int running = 0;  // Condition variable for ISR interupt loop to execute or not. Changed based on user commands from Serial
const int N = 16;
unsigned long bytes = 0;
char command[64];
int commandIndex = 0;

/*=========== 'dataNode' Data Structure Definition ===========*/
/*  Used for new variables the user wants to record. Consists of a 
 *  pointer address, a variable name, units, and a values variable.
 *  Structs allow multiple variables to be grouped under a single 
 *  block of memory, and allow a single pointer to access them.  
 */
   
struct dataNode {         // Custom variable that structures a selected set of data
  double *address;        // Each of these data declarations will be inputted when a dataNode variable is declared
                          //  and used as a temporary storage for the values?
  const char *name, *units;
  double *values;         // Points to an array used as a circular queue for recorded values, NULL for initialized values
  struct dataNode *next;  // the operator '->' is often used to dereference a pointer to a struct (aka access the value pointed to)
} *data = NULL;           // 'data' points to the head of the list of nodes, initially the list is empty
                          // struct{...} *x is synctatically analogous to int *x, and sets aside space for a pointer and assigns a null value
int nodeCount = 0;        // This value is redundant, but makes debugging easier

/*=========== Function for Preprocessor Macros ===========*/
/*  This function is called at the precompiler macro's, with user's input. 
 *  First it generates a datanode pointer 'ptr' and creates storage space for it.
 *  then it allocates memory for values, if record>0. A NULL struct named 'data' was made during
 *  the definition of the dataNode struct, and NULL value acts as the first part of a list
 *  of dataNodes. When a new variable is registered usign this fucntion, the
 *  variable 'data' is always updated to point to the newest dataNode struct. 
 *  Before it is updated, however, the newest dataNode is made to have access to the 
 *  second newest dataNode through the 'ptr->next = data" statement. This allows
 *  iteration through the list of dataNodes by both void loop() and the ISR(). 
 *  
 */  
void register_variable(double *address, const char *name, int record, const char *units) {
  
  struct dataNode *ptr = (struct dataNode *) malloc(sizeof(struct dataNode));  /*  Declare/create storage for new variable of type dataNode 
                                                                                   malloc(size) creates a block of 'size' many bytes
                                                                                   and returns a pointer to beginning of block           */
                                                                                                                                                             
  if (!ptr) for (;;delay(1000)) {  // If pointer is empty for 1000ms, the memory allocation didn't work. This is an inline if-for statement
    Serial.print("ERROR\tregister_variable(): Unable to malloc dataNode, nodeCount = ");
    Serial.print(nodeCount);
    Serial.print(", variable = ");
    Serial.print(name);
    Serial.print("\n");
    Serial.flush();
  }
  
  if (record) {                                         // If the variable being registered was used with RECORD() macro*/ 
    ptr->values = (double *) malloc(N*sizeof(double));  // Allocate memory for recorded values  Allocate memory for recorded values, N set at 16 at storge var block*/
    if (!ptr->values) for (;;delay(1000)) {             // Same timeout method as the allocation for ptr */
      Serial.print("ERROR\tregister_variable(): Unable to malloc values array, nodeCount = ");
      Serial.print(nodeCount);
      Serial.print(", variable = ");
      Serial.print(name);
      Serial.print("\n");
      Serial.flush();
    }
  } else ptr->values = NULL;
  nodeCount++; // increment counter
  ptr->address = address; // address in memory,
  ptr->name = name;     // Given name, char's
  ptr->units = units;   // units, single char
  
  ptr->next = data;  // when the 'next' member of the current node struct is called, it will point to address
                     // of the previous node entered. The first node created will point to NULL                     
  data = ptr;        // address stored in 'data' variable is updated to be the current value of 'ptr'
}

/*======================*/
void setPeriod (int period) {         // period in ms
  const double tick = 1024000 / 16e6; // clock tick in ms
  int number = floor(period / tick) - 1;
  char buf[256];
  sprintf(buf,"DEBUG\tsetPeriod(%d): number = %d, tick = %ld us, actual period = %ld us\n", period, number, (long)(1e3*tick), (long)(1e3*tick*(number+1)));
  Serial.print(buf);
  cli();                    // Disallow interrupts, so that we can manipulate Timer1, which is used with an interrupt
  TCCR1A = 0;               // Set entire TCCR1A register to 0
  TCCR1B = 0;               // Same for TCCR1B
  TCNT1  = 0;               // Initialize Timer1's counter value to be 0
  OCR1A = number;           // = (16*10^6) /(1*1024) - 1 (must be <65536) originally 15624
  TCCR1B |= (1 << WGM12);   // Turn on CTC mode
  TCCR1B |= (1 << CS12) | (1 << CS10);    // Set bits called CS10 and CS12 so that Timer1 uses 1024 prescaler
  TIMSK1 |= (1 << OCIE1A);  // Enable timer compare interrupt
  sei();                    // Re-allow interrupts
}

/*======================*/
void setup() {
  Serial.begin(115200);
  Serial.print("\nBOOT\n");
  Serial.flush();
  TCCR2B = TCCR2B & 0b11111000 | 0x01;
  pinMode(fanPin,OUTPUT);
  userSetup();
}

/*======================*/
ISR(TIMER1_COMPA_vect){ 
/* Timer1 interrupt, 1Hz, toggles pin 13 (LED)
 * Generates pulse wave of frequency 1kHz/2 = 0.5kHz (takes two cycles for full wave- toggle high then toggle low)
 * This code will execute when the timer's counter overflows, which is then reset. 
 * (The timer's counter is different than the variable called 'counter' below)   
 */

  if (!running) return;
  if (counter % 2){
    digitalWrite(fanPin,HIGH);  // Even count, go high
  } else{
    digitalWrite(fanPin,LOW);   // Odd count, go low
  }
  userAction();   // Regularly call userAction()
  for(struct dataNode *ptr = data; ptr; ptr = ptr->next) if (ptr->values) ptr->values[counter % N] = *ptr->address; 
  counter++;
}

/*======================*/
void parseCommand(void) {
  char *ptr; // 8 bytes of memory

  ptr = strtok(command," ");  // returns first token after it splits string 'command' into tokens based on space (" ")delimiter, and 
  if (!ptr) {

    return;
  }
  switch(strlen(ptr)) {
  case 3:
    if (!strcmp(ptr,"SET")) { // Equals zero if strings are equal. Will set values based on user input
      ptr = strtok(NULL," "); // Since we passed NULL as the argument, strtok returns second token of 'command'

      if (!ptr) {
        return;
      }
      for(struct dataNode *dptr = data; dptr; dptr = dptr->next) if (!strcmp(dptr->name,ptr)) { // strcmp is 0 when the strings are equal
        ptr = strtok(NULL," "); // third token of 'command'
        if (!ptr) {

          return;
        }

        double ivalue;
        int exponent;
        ivalue = atof(ptr); // replaced since sscanf() wasn't working, and atof() works well with floats.
       // sscanf(ptr,"%ld",&ivalue); // ld means it's supposed to be a long int in base 10, reads data from string 'ptr' and stores them into &ivalue according the parameter '%ld' (long int)
        if (ivalue == 0) {
          *dptr->address = 0;
          return;
        } 
        
      /*  else {
       *   ptr = strtok(NULL," "); // fourth token of 'command'
       *   Serial.print("ptr 4: ");
       *   Serial.println(ptr);      ====== OLD CODE, COMMENTED OUT, LEFT IN CASE IT'S NEEDED IN FUTURE =====
       *   if (!ptr) {
       *    return;
       *   }
       */
       
         // sscanf(ptr,"%d",&exponent); //reads pointer value into exponent address, d indicates a decimal integer         
          *dptr->address = ivalue; //* pow(2,exponent);

        //}

        return;
      }
    }
  case 4:
    if (!strcmp(ptr,"STOP")) {
      running = 0;
      userStop();
      return;
    }
  case 5:
    if (!strcmp(ptr,"START")) {
      setPeriod(1000*dt);
      counter = 0;
      oc = 0;
      userStart();
      running = 1;
      return;
    }
  case 9:
    if (!strcmp(ptr,"HANDSHAKE")) {// Here is where Arduino sends info to controller on variables to be initialized
      ptr = strtok(NULL," ");      
      Serial.print("\nHANDSHAKE\n"); // Do a readline() in Python to clear this all 
      Serial.flush();
      for(struct dataNode *ptr = data; ptr; ptr = ptr->next) if (!ptr->values) { // Send if there are no values, unlike in loop
        Serial.print("INIT\t");
        Serial.print(ptr->name);
        Serial.print ("\t=\t");
        Serial.print(*((long *)ptr->address),HEX);
        //Serial.print(*ptr->address);
        Serial.print("\t");
        Serial.print(ptr->units);
        Serial.print("\n");
        Serial.flush();
      }
      Serial.print("\nREADY\n");
      Serial.flush();
      return;
    }
  }


  return;
}

/*======================*/
/* Called if there is anything in the serial line. It ultimately calls parseCommand, which can be found above */
void getCommand() { 
  static unsigned char ch;
  static int discard = 0;
  Serial.readBytes(&ch,1);
#ifdef DEBUG
  Serial.print("DEBUG\tgetCommand() : ch = ");
  Serial.print(ch, BIN);
  Serial.print("\n");
  Serial.flush();
#endif
  if (discard && (ch == '\n')) { // reached end of garbage (hopefully \n was not garbage?!
    discard = 0;
    return;
  }
  if (discard) return;
  if (ch & 0x80) {
    command[commandIndex] = 0;
    Serial.print("ERROR\tMSB set in input stream, command so far = \"");
    Serial.print(command);
    Serial.print("\"\n");
    Serial.flush();
    commandIndex = 0;
    discard = 1;
    return;
  }
  Serial.write(ch | 0x80);
  if (ch == '\n') {
    command[commandIndex] = 0;
    parseCommand();
    commandIndex = 0;
    ch = 0;
    return;
  }
  command[commandIndex++] = ch;
}

/*======================*/
/* void loop() here is used just to send and receive data alog the serial line. */
/* Is looping alongside with the ISR code. */
void loop() {
  char buf[256];
  if (Serial.available()) getCommand();
  if ((counter - oc) > N) {
    Serial.print("ERROR\tInternal buffer overrun\n");
  }  
  while (oc < counter) { /* 'counter' is incremented every time the ISR is called for Timer1. 
                          *  This avoids mis-matching the index/counter and the data. 
                          */
    Serial.println("");
    Serial.print("INDEX\t");
    Serial.print(oc);
    Serial.print("\t");
    Serial.print(counter);
    Serial.print("\n"); 
    Serial.flush();
    for(struct dataNode *ptr = data; ptr; ptr = ptr->next) if (ptr->values) { // Send if there are values, unlike in handshake
      Serial.print("VALUE\t");
      Serial.print(ptr->name);
      Serial.print("\t=\t");
      Serial.print(*((long *)&ptr->values[oc % N]), HEX);
      Serial.print("\t");
      Serial.print(ptr->units);
      Serial.print("\n");
      Serial.flush();
    }
    oc++;
  }
}
