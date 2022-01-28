A little pandemic project to build a
[DHC-2 Beaver](https://en.wikipedia.org/wiki/De_Havilland_Canada_DHC-2_Beaver)
cockpit in the basement.


This repo contains the software used for the integration, with miscellaneous other notes.

The panel instruments are displayed with [AirPlayer](https://siminnovations.com/)
running on a Raspberry Pi 3.  The Pi also monitors various physical inputs
via an Arduino Mega connected by USB.

The Arduino Mega runs the sketch in `controlpanel/controlpanel.ino`
and manages a switch panel with up to 32 digital pins,
along with a collection of (push-button) rotary encoders on the instrument panel.
The encoders are managed by a GPIO breakout board like this one
[MCP23017](https://www.amazon.ca/Waveshare-MCP23017-Expansion-Interface-Expands/dp/B07P2H1NZG/ref=pd_lpo_147_t_2/142-1911766-2859153).
Each encoder requires three pins so a 16-pin breakout
hosts up to five encoders, and can be daisy chained (up to 8 boards I believe).
The Arduino tracks encoder changes via interrupt,
and provides accumulated change along with current switch state on demand via the serial protocol.

The logical mapping of switches from the Arduino pins is configured in `switchmap.py`,
and `serialmonitor.py` runs a very simple polling routine which checks for state changes
on a regular basis.

TODO: this will also forward the input actions to FS2020 via python-simconnect.




Install miniconda on the PI:

https://stackoverflow.com/questions/39371772/how-to-install-anaconda-on-raspberry-pi-3-model-b

    wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh
    md5sum Miniconda3-latest-Linux-armv7l.sh
    /bin/bash Miniconda3-latest-Linux-armv7l.sh
    rm Miniconda3-latest-Linux-armv7l.sh

Set up the conda environment for the serial monitor:

    conda config --add channels rpi

    conda env update -f environment.yml


Tool to disable mouse pointer unless moving

    sudo apt-get install unclutter





https://raspberrypi.stackexchange.com/questions/111642/raspberry-pi-4-framerate-drop-with-video-on-chromium-browser



raspi-config => enable "Wait for network at boot"


# See https://www.linuxuprising.com/2021/04/how-to-enable-hardware-acceleration-in.html
# note display is always 0, window position gives offset between screens
# user-data-dir forces second profile to get second window
CHROMIUM_OPTS=--display=:0 --kiosk --start-fullscreen --incognito --noerrdialogs --no-first-run --disable-translate --disable-features=TranslateUI,TouchpadOverscrollHistoryNavigation --disable-pinch --ignore-gpu-blocklist --enable-accelerated-video-decode --enable-gpu-rasterization

# start main nav instruments
chromium-browser $CHROMIUM_OPTS --window-position=0,0 --user-data-dir=/home/pi/chromium-profiles/screen0 http://192.168.2.136:8000/panels/dhc2-nav.html 2>&1 > /home/pi/screen0.log &

# start center instrument panel
chromium-browser $CHROMIUM_OPTS --window-position=1024,0 --user-data-dir=/home/pi/chromium-profiles/screen1 http://192.168.2.136:8000/panels/dhc2-center.html 2>&1 > /home/pi/screen1.log &




Create ~/.config/lxsession/LXDE-pi/autostart containing:

    /home/pi/dhc2-beaver-sim/startup.sh


On restart, logs are found in:

     ~/.cache/lxsession/LXDE-pi/run.log



https://reelyactive.github.io/diy/pi-kiosk/



setup rpi screens (via gui display configuration or cli):


$ tvservice -l
2 attached device(s), display ID's are :
Display Number 2, type HDMI 0
Display Number 7, type HDMI 1

$ tvservice -s -v 2
state 0x6 [DVI CUSTOM RGB full 4:3], 1024x768 @ 75.00Hz, progressive

$ tvservice -m DMT -v 2
Group DMT has 6 modes:
           mode 4: 640x480 @ 60Hz 4:3, clock:25MHz progressive
           mode 6: 640x480 @ 75Hz 4:3, clock:31MHz progressive
           mode 9: 800x600 @ 60Hz 4:3, clock:40MHz progressive
           mode 11: 800x600 @ 75Hz 4:3, clock:49MHz progressive
  (prefer) mode 16: 1024x768 @ 60Hz 4:3, clock:65MHz progressive
           mode 18: 1024x768 @ 75Hz 4:3, clock:78MHz progressive

$ tvservice -s -v 7
state 0xa [HDMI CUSTOM RGB full 4:3], 1024x768 @ 75.00Hz, progressive

$ tvservice -m DMT -v 7
Group DMT has 11 modes:
           mode 4: 640x480 @ 60Hz 4:3, clock:25MHz progressive
           mode 5: 640x480 @ 72Hz 4:3, clock:31MHz progressive
           mode 6: 640x480 @ 75Hz 4:3, clock:31MHz progressive
           mode 8: 800x600 @ 56Hz 4:3, clock:36MHz progressive
           mode 9: 800x600 @ 60Hz 4:3, clock:40MHz progressive
           mode 10: 800x600 @ 72Hz 4:3, clock:50MHz progressive
           mode 11: 800x600 @ 75Hz 4:3, clock:49MHz progressive
           mode 16: 1024x768 @ 60Hz 4:3, clock:65MHz progressive
           mode 17: 1024x768 @ 70Hz 4:3, clock:75MHz progressive
           mode 18: 1024x768 @ 75Hz 4:3, clock:78MHz progressive
           mode 85: 1280x720 @ 60Hz 16:9, clock:74MHz progressive


g3py> uvicorn metrics:app --reload --host 0.0.0.0

rpi4> DISPLAY=:0 chromium-browser --new-window --window-position=0,0 --kiosk --app=http://192.168.2.136:8000/panels/dhc2-nav.html

DISPLAY=:0 chromium-browser --kiosk --app=http://192.168.2.136:8000/panels/dhc2-nav.html

rpi4> DISPLAY=:0 chromium-browser --new-window --window-position=1024,0 --kiosk --app=http://192.168.2.136:8000/panels/dhc2-center.html




--user-data-dir="/home/pi/Documents/Profiles/0"











Finding specific LCD panels.

Viewable area, outline area often constrained

Find common sizes (diagonal) via something like https://www.panelook.com/modelsearch.php?op=size

Figure out a size and aspect ratio that suits your needs (e.g. https://en.wikipedia.org/wiki/Display_size)

Either find a used monitor with the right size to disassemble,
or get a bare LCD panel on ebay, along with a matching controller board.

19" monitor for main instrument panel - LG Flatron E1911TX, jumped power switch with a secondary push button


center panel:  LP156WH4-TLP2  + controller https://www.ebay.ca/itm/163835481523


Useful links (YMMV)
---

- https://www.dhc-2.com/current_cover_page.htm

- [Sim Innovations - Flight simulation solutions](https://siminnovations.com/)
- [SimVimCockpit - Configurator](https://simvim.com/)
- [MobiFlight + Arduino + Your Favorite Flight Simulator = Your Home Cockpit!](https://www.mobiflight.com/en/index.html)
- [DHC-2 Beaver](https://store.x-plane.org/DHC-2-Beaver_p_395.html) - xplane model
- [DHC-2 Beaver](https://milviz.com/flight/products/DHC2/)- FSX, Prepar3D
- [Cessna 172 Flight Simulator Panel](https://cessna172sim.allanglen.com/) - thingiverse parts
- [Cessna 172 Cockpit](https://flyingforfun.weebly.com/cessna-172-cockpit.html/) - servo-driven wet compass etc
- [McMaster-Carr](https://www.mcmaster.com/telescoping-tubing/steel-bolt-together-framing-and-fittings/) steel bolt-together framing
[Accueil - MxLab Designs - Impression 3D Printing à La Prairie](https://www.mxlabdesigns.ca/)
- [Street and Racing Seats](http://www.performance-world.com/Street-and-Racing-Seats-s/1872.htm) or junkyard 2 x compact/subcompact two manual adjust front bucket seats on slider tracks https://centredelautovince.wixsite.com/vincentauto
- [GitHub - clearwater/SwitecX25: Arduino library for Switec X25.168 and friends](https://github.com/clearwater/SwitecX25)  plus “Speedometer Gauge Needles”
- or hack say a voltmeter gauge? [Equus 6268 Voltmeter, Voltmeter - Amazon Canada](https://www.amazon.ca/Equus-6268-Voltmeter/dp/B000EVU8YS/ref=sr_1_1?dchild=1&keywords=Equus+6268&qid=1617119590&s=automotive&sr=1-1)
[GitHub - adafruit/Adafruit-MCP23017-Arduino-Library](https://github.com/adafruit/Adafruit-MCP23017-Arduino-Library/)
[GitHub - maxgerhardt/rotary-encoder-over-mcp23017: Library and example code with which one can controll multiple rotary encoders over the MCP23017 I2C GPIO expander.](https://github.com/maxgerhardt/rotary-encoder-over-mcp23017)
