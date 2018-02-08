import os
import subprocess
import time

STARTUP_WAV = "media/startup.wav"

# TF2 sounds
# SCAN_WAV = "media/tf2/sentry_scan2.wav"
# TARGET_ACQUIRED_WAV = "media/tf2/sentry_spot_client.wav"

# Portal sounds
# STARTUP_WAV = "media/portal/Turret_sentry_mode_activated.wav"
SCAN_WAV = "media/portal/Turret_ping.wav"
SHUTTING_DOWN_WAV = "media/portal/Turret_shutting_down.wav"

TARGET_ACQUIRED_WAV = "media/portal/Turret_target_acquired.wav"
TARGET_ACQUIRED_WAV_2 = "media/portal/Turret_there_you_are.wav"
TARGET_ACQUIRED_WAV_3 = "media/portal/Turret_I_see_you.wav"
TARGET_ACQUIRED_WAV_4 = "media/portal/GLaDOS_surprise.wav"
TARGET_ACQUIRED_WAV_5 = "media/portal/Turret_there_you_are_2.wav"

TARGET_LOST_WAV = "media/portal/Turret_target_lost.wav"

HELLO_FRIEND_WAV = "media/portal/Turret_hello_friend.wav"
HELLO_FRIEND_WAV_2 = "media/portal/Turret_can_i_help_you.wav"

CLICK = "media/portal/Turret_click.wav"
CLICK_2 = "media/portal/Turret_click_2.wav"
CLICK_3 = "media/portal/Turret_click_3.wav"
CLICK_4 = "media/portal/Turret_click_4.wav"
CLICK_5 = "media/portal/Turret_click_5.wav"
CLICK_6 = "media/portal/Turret_click_6.wav"

procmap = {
    'wav': 'aplay ',
    'mp3': 'mpg123 -q'
}


def play(soundfile, blocking=True):
    ext = soundfile.lower().strip()[-3:]
    print(ext)
    if(ext in procmap.keys()):
        proc = procmap[ext]
    else:
        print("Unrecognized file format: '" + ext.upper()+"'")
        return False

    print(proc + soundfile + ("" if blocking else " &"))

    loc = os.path.dirname(os.path.realpath(__file__))

    # probably doesn't escape weird path characters, spaces, etc. properly
    p = subprocess.call(proc + soundfile + ("" if blocking else " &"),
                        shell=True, cwd=loc)
    return p


if (__name__ == "__main__"):
    while(True):
        play("media/portal/GLaDOS_init_surprise.wav", True)
        print("returned")
        time.sleep(1.5)
