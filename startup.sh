#!/bin/bash
export DISPLAY=:0
xset -dpms     # disable DPMS (Energy Star) features.
xset s off     # disable screen saver
xset s noblank # don't blank the video device
unclutter &    # hide X mouse cursor unless mouse activated

source /home/pi/miniconda3/bin/activate beaver-sim

# begin monitoring arduino
cd /home/pi/dhc2-beaver-sim
python -u serialmonitor.py 2>&1 > serialmonitor.log &

# See https://www.linuxuprising.com/2021/04/how-to-enable-hardware-acceleration-in.html
# note display is always 0, window position gives offset between screens
# user-data-dir forces second profile to get second window



CHROMIUM_OPTS="--display=:0 --kiosk --start-fullscreen --incognito --noerrdialogs --no-first-run --disable-translate --disable-features=TranslateUI,TouchpadOverscrollHistoryNavigation --disable-pinch --ignore-gpu-blacklist"
# other opts:
# --enable-gpu-rasterization - cause screen artifacts
# --enable-accelerated-video-decode - not needed?

G3PY_HOST=http://simba.local:8000

# start main nav instruments
chromium-browser $CHROMIUM_OPTS --window-position=0,0 --user-data-dir=/home/pi/chromium-profiles/screen0 $G3PY_HOST/panels/dhc2-nav.html 2>&1 > /home/pi/screen0.log &

# start center instrument panel
chromium-browser $CHROMIUM_OPTS --window-position=1024,0 --user-data-dir=/home/pi/chromium-profiles/screen1 $G3PY_HOST/panels/dhc2-center.html 2>&1 > /home/pi/screen1.log &
