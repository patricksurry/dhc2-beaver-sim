#include <ShiftRegister74HC595.h>
#include <Adafruit_MCP23X17.h>

#include "rotary.h"

// Control panel initialization

const unsigned char arduinoInterruptPin = 3, ledPin = 13;
// 7 is the jumper setting a0, a1, w2 given the board address 0x27 == 0x20 | a0,a1,a2
const unsigned char mcpBoardAddress = 7;

// object representing the expansion board
Adafruit_MCP23X17 mcp;

// a buffer where we'll mirror mcp data
uint16_t mcpBits;

// ShiftRegister74HC595<numberOfShiftRegisters> sr(serialDataPin, clockPin, latchPin);
// 12V leds are wired to a shift register 
ShiftRegister74HC595<1> sr(12, 11, 10);

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
  for (i=52; i>=22; i--) v = (v << 1) | (1-digitalRead(i));
  return v;
}

byte analogVals[20];  // 16*10/8 = 20

void readAnalogInputs() {
  byte* p = analogVals;
  
  uint32_t val = 0;
  int offset = 0;
  
  for (int i=0; i<16; i++) {
    val |= analogRead(i) << offset;
    offset += 10;
    while (offset >= 8) {
      *(p++) = val & 0xff;
      val >>= 8;
      offset -= 8;
    }
  }
}


void setLEDs(unsigned char bits) {
  // flip high bits since mofsets are inverted
  unsigned char actual = bits ^ B11110000;

  sr.setAll(&actual);
}


void serialEvent() {
  // event handler for incoming serial data
  unsigned char cmd;
  uint32_t switchState;
  unsigned char knobState[nKnobs];
  unsigned char ledState;

  // our protocol currently just has one command...
  Serial.readBytes(&cmd, 1);

  switch(cmd) {
    case 0x01:   // Read input state: () => 24 bytes output
      // returns:
      // 4 bytes of switch status (32 bits)
      // one byte per encoder (high bit switch with 7 bits signed movement)
      // 20 bytes of analog input (16 * 10 bits)
      switchState = getSwitches();
      for (int i=0; i<nKnobs; i++) knobState[i] = knobs[i].read();
      readAnalogInputs();
      Serial.write((byte*)&switchState, sizeof(switchState));
      Serial.write((byte*)&knobState, nKnobs);
      Serial.write(analogVals, sizeof(analogVals));
      break;
    case 0x02: // Set output state: 1 byte => () output
      Serial.readBytes(&ledState, 1);
      setLEDs(ledState);
      break;
  }
}


void setup() {
    int i;

    pinMode(arduinoInterruptPin, INPUT);
//    pinMode(ledPin, OUTPUT);  // use the p13 LED as debugging

    Serial.begin(115200);

    setLEDs(0);

    // set pullup resistors for switch panel inputs wired to mega pins 22-53
    for (i=22; i<54; i++) pinMode(i, INPUT_PULLUP);

    // also set pullup resistors for analog inputs if want relatively constant for unused
    // for (i=54; i<70; i++) pinMode(i, INPUT_PULLUP);

    // set up the expansion board
    // https://www.waveshare.com/w/upload/8/8e/MCP2307_IO_Expansion_Board_User_Manual_EN.pdf
    mcp.begin_I2C(mcpBoardAddress);
    mcp.setupInterrupts(true, false, LOW);
    for (i=0; i<16; i++) {
      mcp.pinMode(i, INPUT_PULLUP);
      mcp.setupInterruptPin(i, CHANGE);
    }
    // clear any existing mcp interrupt by reading current state
    processEncoders();

    mcpEnableInterrupts();
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
