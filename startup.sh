#!/bin/sh
export DISPLAY=:0
xset -dpms     # disable DPMS (Energy Star) features.
xset s off     # disable screen saver
xset s noblank # don't blank the video device
unclutter &    # hide X mouse cursor unless mouse activated

source activate beaver-sim

# begin monitoring arduino
python serialmonitor.py 2>&1 > serialmonitor.log &

# start main nav instruments
# note display is always 0, window position gives offset between screens
# user-data-dir forces second profile to get second window
chromium-browser --display=:0 --kiosk --start-fullscreen --incognito --noerrdialogs --no-first-run --disable-translate --disable-features=TranslateUI,TouchpadOverscrollHistoryNavigation --disable-pinch --window-position=0,0 --user-data-dir=/home/pi/chromium-profiles/screen0 http://192.168.2.136:8000/panels/dhc2-nav.html 2>&1 > /home/pi/screen0.log &

# start center instrument panel
chromium-browser --display=:0 --kiosk --start-fullscreen --incognito --noerrdialogs --no-first-run --disable-translate --disable-features=TranslateUI,TouchpadOverscrollHistoryNavigation --disable-pinch --window-position=1024,0 --user-data-dir=/home/pi/chromium-profiles/screen1 http://192.168.2.136:8000/panels/dhc2-center.html 2>&1 > /home/pi/screen1.log &

