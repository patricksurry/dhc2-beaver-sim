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

Compile:

    arduino-cli compile --fbqn <fbqn> <sketch>


Upload:

    arduino-cli upload -p <port> --fqbn <fqbn> <sketch>
