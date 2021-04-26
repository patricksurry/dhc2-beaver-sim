#include <Adafruit_MCP23017.h>

//---------- Rotary encoder code adapted from  https://github.com/brianlow/Rotary

#define HALF_STEP

// Values returned by 'process'
// No complete step yet.
#define DIR_NONE 0x0
// Clockwise step.
#define DIR_CW 0x1
// Counter-clockwise step.
#define DIR_CCW 0x2


class Rotary
{
  public:
    Rotary(unsigned char, unsigned char, unsigned char, unsigned char (*)(unsigned char) = digitalRead);
    unsigned char process();
    unsigned char read();
  private:
    unsigned char state;
    unsigned char switchstate;
    unsigned char accum;
    unsigned char pin1;
    unsigned char pin2;
    unsigned char pin_switch;
    unsigned char (*pinReader)(unsigned char);
};


/*
 * The below state table has, for each state (row), the new state
 * to set based on the next encoder output. From left to right in,
 * the table, the encoder outputs are 00, 01, 10, 11, and the value
 * in that position is the new state to set.
 */

#define R_START 0x0

#ifdef HALF_STEP
// Use the half-step state table (emits a code at 00 and 11)
#define R_CCW_BEGIN 0x1
#define R_CW_BEGIN 0x2
#define R_START_M 0x3
#define R_CW_BEGIN_M 0x4
#define R_CCW_BEGIN_M 0x5
const unsigned char ttable[6][4] = {
  // R_START (00)
  {R_START_M,            R_CW_BEGIN,     R_CCW_BEGIN,  R_START},
  // R_CCW_BEGIN
  {R_START_M | (DIR_CCW << 4), R_START,        R_CCW_BEGIN,  R_START},
  // R_CW_BEGIN
  {R_START_M | (DIR_CW << 4),  R_CW_BEGIN,     R_START,      R_START},
  // R_START_M (11)
  {R_START_M,            R_CCW_BEGIN_M,  R_CW_BEGIN_M, R_START},
  // R_CW_BEGIN_M
  {R_START_M,            R_START_M,      R_CW_BEGIN_M, R_START | (DIR_CW << 4)},
  // R_CCW_BEGIN_M
  {R_START_M,            R_CCW_BEGIN_M,  R_START_M,    R_START | (DIR_CCW << 4)},
};
#else
// Use the full-step state table (emits a code at 00 only)
#define R_CW_FINAL 0x1
#define R_CW_BEGIN 0x2
#define R_CW_NEXT 0x3
#define R_CCW_BEGIN 0x4
#define R_CCW_FINAL 0x5
#define R_CCW_NEXT 0x6

const unsigned char ttable[7][4] = {
  // R_START
  {R_START,    R_CW_BEGIN,  R_CCW_BEGIN, R_START},
  // R_CW_FINAL
  {R_CW_NEXT,  R_START,     R_CW_FINAL,  R_START | (DIR_CW << 4)},
  // R_CW_BEGIN
  {R_CW_NEXT,  R_CW_BEGIN,  R_START,     R_START},
  // R_CW_NEXT
  {R_CW_NEXT,  R_CW_BEGIN,  R_CW_FINAL,  R_START},
  // R_CCW_BEGIN
  {R_CCW_NEXT, R_START,     R_CCW_BEGIN, R_START},
  // R_CCW_FINAL
  {R_CCW_NEXT, R_CCW_FINAL, R_START,     R_START | (DIR_CCW << 4)},
  // R_CCW_NEXT
  {R_CCW_NEXT, R_CCW_FINAL, R_CCW_BEGIN, R_START},
};
#endif

/*
 * Constructor. Each arg is the pin number for each encoder contact.
 */
Rotary::Rotary(unsigned char _pin_switch, unsigned char _pin1, unsigned char _pin2, unsigned char (*f)(unsigned char)) {
  // Assign variables.
  pin_switch = _pin_switch;
  pin1 = _pin1;
  pin2 = _pin2;
  pinReader = f;
  // Initialise state.
  state = R_START;
  switchstate = 0;
  accum = 0;
}

unsigned char Rotary::read() {
  // consume accumulated rotation and reset to 0, returning change and latest switch state
  // return value is a byte with high bit indicating switch state, and 7 lsb giving a
  // twos-complement signed value for the rotation offset since last read()
  // this gives up to +/- 63 detents per read() which is enough for polling at a few times per second
  unsigned char v = (accum & 0x7f)  | (switchstate << 7);
  accum = 0;
  return v;
}

unsigned char Rotary::process() {
  // Grab state from on-board digital input pins
  unsigned char pinstate = (pinReader(pin2) << 1) | pinReader(pin1);
  switchstate = pinReader(pin_switch) ? 0: 1; // flip switch sign - active pullup is 0
  // Determine new state from the pins and state table.
  state = ttable[state & 0xf][pinstate];
  // Return high nibble emit bits, ie the generated event.
  unsigned char dir = state >> 4;
  if (dir) accum += (dir == DIR_CW) ? 1 : -1;
  return  (switchstate << 2) | dir;
}

// ---------- end rotary encoder


// Control panel initialization

const unsigned char arduinoInterruptPin = 3, ledPin = 13;
// 7 is the jumper setting a0, a1, w2 given the board address 0x27 == 0x20 | a0,a1,a2
const unsigned char mcpBoardAddress = 7;

// object representing the expansion board
Adafruit_MCP23017 mcp;

// a buffer where we'll mirror mcp data
uint16_t mcpBits;

unsigned char mcpBitReader(unsigned char bit) {
    // helper function that reads a bit from mcpBits buffer
    return bitRead(mcpBits, bit);
}

// flag when expansion board has updated data
volatile boolean mcpInterrupted = false;

// rotary encoders wired to the expansion board
Rotary knobs[] = {
  Rotary(8+0, 8+1, 8+2, mcpBitReader),  // B0,1,2
  Rotary(8+3, 8+4, 8+5, mcpBitReader),  // B3,4,5
  Rotary(8+6, 8+7, 7, mcpBitReader),    // B6,7,A7
  Rotary(6, 5, 4, mcpBitReader),        // A6,4,5
  Rotary(3, 2, 1, mcpBitReader)         // A3,2,1
};
const int nKnobs = sizeof(knobs)/sizeof(Rotary);

void setup() {
    int i;

    pinMode(arduinoInterruptPin, INPUT);
//    pinMode(ledPin, OUTPUT);  // use the p13 LED as debugging

    Serial.begin(115200);

    // set pullup resistors for switch panel inputs wired to mega pins 22-52
    for (i=22; i<53; i++) pinMode(i, INPUT_PULLUP);

    // set up the expansion board
    // https://www.waveshare.com/w/upload/8/8e/MCP2307_IO_Expansion_Board_User_Manual_EN.pdf
    mcp.begin(mcpBoardAddress);
    mcp.setupInterrupts(true, false, LOW);
    for (i=0; i<16; i++) {
      mcp.pinMode(i, INPUT);
      mcp.pullUp(i, HIGH);
      mcp.setupInterruptPin(i, CHANGE);
    }
    // clear any existing mcp interrupt by reading current state
    processEncoders();

    mcpEnableInterrupts();
}

void mcpEnableInterrupts() {
    mcpInterrupted = false;
    // EIFR=0x01; /* force arduino interrupt state low, doesn't seem needed? */
    attachInterrupt(digitalPinToInterrupt(arduinoInterruptPin), mcpInterruptHandler, FALLING);
}

void mcpDisableInterrupts() {
    detachInterrupt(digitalPinToInterrupt(arduinoInterruptPin));
}

void mcpInterruptHandler() {
    // interrupt handler simply sets a volatile flag that we'll notice in loop()
    mcpInterrupted = true;
}

void processEncoders() {
  // update current state of all the rotary encoders after an interrupt indicating a change
  // reading the state of all pins also clears interrupt state (see datasheet)
  mcpBits = mcp.readGPIOAB();
  // update all the encoder states
  for (int i=0; i < nKnobs; i++) (void)knobs[i].process();
}

uint32_t getSwitches() {
  // grab current value of all the panel switches, flipping active low => 1
  unsigned long v=0;
  int i;
  for (i=52; i>=22; i--) v = v*2 + (1-digitalRead(i));
  return v;
}

void serialEvent() {
  // event handler for incoming serial data
  unsigned char cmd;
  uint32_t switchState;
  unsigned char knobState[nKnobs];

  // our protocol currently just has one command...
  Serial.readBytes(&cmd, 1);

  switch(cmd) {
    case 0x01:
      // return 4 bytes of switch status, plus one byte per encoder
      switchState = getSwitches();
      for (int i=0; i<nKnobs; i++) knobState[i] = knobs[i].read();
      Serial.write((byte*)&switchState, sizeof(switchState));
      Serial.write((byte*)&knobState, nKnobs);
      break;
  }
}

void loop() {
  // all we do here is check whether an interrupt fired for encoders,
  // and temporarily disable while we update encoder state
  // incoming client commands are captured in serialEvent()
  if (mcpInterrupted) {
    mcpDisableInterrupts();
    processEncoders();
    mcpEnableInterrupts();
  }
}
