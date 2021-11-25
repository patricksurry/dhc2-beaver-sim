#include "rotary.h"

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
