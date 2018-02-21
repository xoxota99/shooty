import os
import subprocess
import time
import sys

STARTUP = "media/startup.wav"

# TF2 sounds
# SCAN = "media/tf2/sentry_scan2.wav"
# TARGET_ACQUIRED = "media/tf2/sentry_spot_client.wav"

# Portal sounds
# STARTUP = "media/portal/Turret_sentry_mode_activated.wav"
SCAN2 = "media/portal/Turret_ping.wav"
SCAN = "media/tf2/sentry_scan2.wav"
SHUTTING_DOWN = "media/portal/Turret_shutting_down.wav"

TARGET_ACQUIRED = "media/portal/Turret_target_acquired.wav"
TARGET_ACQUIRED_2 = "media/portal/Turret_there_you_are.wav"
TARGET_ACQUIRED_3 = "media/portal/Turret_I_see_you.wav"
TARGET_ACQUIRED_4 = "media/portal/GLaDOS_surprise.wav"
TARGET_ACQUIRED_5 = "media/portal/Turret_there_you_are_2.wav"

TURRET_FIRE = "media/portal/Turret_fire.wav"
TURRET_FIRE_2 = "media/portal/Turret_fire_2.wav"
TURRET_FIRE_3 = "media/portal/Turret_fire_3.wav"

TARGET_LOST = "media/portal/Turret_target_lost.wav"

TURRET_ACTIVATED = "media/portal/Turret_sentry_mode_activated.wav"

HELLO_FRIEND = "media/portal/Turret_hello_friend.wav"
HELLO_FRIEND_2 = "media/portal/Turret_can_i_help_you.wav"

CLICK = "media/portal/Turret_click.wav"
CLICK_2 = "media/portal/Turret_click_2.wav"
CLICK_3 = "media/portal/Turret_click_3.wav"
CLICK_4 = "media/portal/Turret_click_4.wav"
CLICK_5 = "media/portal/Turret_click_5.wav"
CLICK_6 = "media/portal/Turret_click_6.wav"


play_proc_map = {
    'darwin': {
        'wav': 'afplay',
        'mp3': 'afplay',
        'ogg': 'ogg123'
    },
    'win32': {},
    'linux': {
        'wav': 'aplay',
        'mp3': 'mpg123 -q'
    }
}


VOLUME = 100
platform = sys.platform
if(platform.startswith("linux")):
    platform = "linux"


def play(soundfile, blocking=True):
    ext = soundfile.lower().strip()[-3:]

    if(ext in play_proc_map[platform].keys()):
        proc = play_proc_map[platform][ext]
    else:
        print("Unrecognized file format: '" + ext.upper()+"'")
        return False

    # print(proc + soundfile + ("" if blocking else " &"))

    loc = os.path.dirname(os.path.realpath(__file__))

    # probably doesn't escape weird path characters, spaces, etc. properly
    p = subprocess.call(proc + " " + soundfile + ("" if blocking else " &"),
                        shell=True, cwd=loc)

    return p


def mute(state=True):
    """
        Mute / unmute sounds. NOTE: This controls Master volume. All audio
        sources will be affected.
    """

    proc = {
        'darwin': lambda: "osascript -e 'set volume output muted "
        + ("true" if state else "false") + "'",
        'linux': lambda: "amixer sset PCM "
        + ("mute" if state else "unmute") + " &",
        'win32': lambda: "nircmd.exe mutesysvolume "
        + ("0" if state else "1") + " &",
    }[platform](),

    p = subprocess.call(proc, shell=True)
    return p


def volume(pcnt):
    """
        This controls Master volume. All audio
        sources will be affected.
        :param pcnt - Percent volume to set, as an integer
        between 1-100.
    """

    proc = {
        'darwin': lambda: 'osascript -e "set volume {:.2f}"'
        .format(7*pcnt/100),
        'linux': lambda: "amixer sset PCM {}% &"
        .format(pcnt),
        'win32': lambda: "nircmd.exe setsysvolume {}"
        .format(int(65535*pcnt/100)),
    }[platform](),

    p = subprocess.call(proc, shell=True)

    return p


# mute(False)
volume(VOLUME)  # initialize volume

if (__name__ == "__main__"):
    while(True):
        print("===PLAY (MP3, Volume 90%)===\n")
        volume(90)
        play("media/test.mp3", True)
        print("returned\n")
        time.sleep(1.5)

        print("===PLAY (WAV, MUTE)===\n")
        mute()
        play("media/portal/GLaDOS_init_surprise.wav", True)
        print("returned\n")
        time.sleep(1.5)

        print("===PLAY (WAV, UNMUTE)===\n")
        mute(False)
        play("media/portal/GLaDOS_init_surprise.wav", True)
        print("returned\n")
        time.sleep(1.5)

        print("===PLAY (WAV, Volume 70%)===\n")
        volume(70)
        play("media/portal/GLaDOS_init_surprise.wav", True)
        print("returned\n")
        time.sleep(1.5)

        print("===PLAY (WAV, Volume 80%)===\n")
        volume(80)
        play("media/portal/GLaDOS_init_surprise.wav", True)
        print("returned\n")
        time.sleep(1.5)
