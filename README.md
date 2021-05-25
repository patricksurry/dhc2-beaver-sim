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


Finding specific panels.

Viewable area, outline area often constrained

Find common sizes (diagonal) via something like https://www.panelook.com/modelsearch.php?op=size

Figure out a size and aspect ratio that suits your needs (e.g. https://en.wikipedia.org/wiki/Display_size)

Either find a used monitor with the right size to disassemble,
or get a bare LCD panel on ebay, along with a matching controller board.

19" monitor for main instrument panel - LG Flatron E1911TX, jumped power switch with a secondary push button



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
