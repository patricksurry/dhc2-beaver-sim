Compile and install sketch from pi@rpi4-panels.locals via `ssh` using
[arduino-cli](https://arduino.github.io/arduino-cli/0.20/)

Install CLI tooling:

    curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh


Init config files and lib indices:

    arduino-cli config init

    > Config file written to: /home/pi/.arduino15/arduino-cli.yaml

    arduino-cli core update-index


Show connected boards (use listall if connected board shows as unknown)

    arduino-cli board list

Port         Protocol Type              Board Name                FQBN             Core
/dev/ttyACM0 serial   Serial Port (USB) Arduino Mega or Mega 2560 arduino:avr:mega arduino:avr


Install platform:

    arduino-cli core install arduino:avr


Install libs:

    arduino-cli lib install ShiftRegister74HC595
    arduino-cli lib install "Adafruit MCP23017 Arduino Library"

Compile:

    cd controlpanel
    arduino-cli compile -b arduino:avr:mega --export-binaries controlpanel.ino

Upload:

    arduino-cli upload -p /dev/ttyACM0 -b arduino:avr:mega controlpanel.ino
