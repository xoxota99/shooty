import os
import subprocess
import time
import helper
import logging
from config import cfg

logger = logging.getLogger(__name__)


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

BLOCKING = 1
NON_BLOCKING = 0

VOLUME_SCALE_MIN = cfg.getint("sounds", "VOLUME_SCALE_MIN")
VOLUME_SCALE_MAX = cfg.getint("sounds", "VOLUME_SCALE_MAX")

play_proc_map = {
    'wav': cfg.get("sounds", "CMD_PLAY_WAV"),
    'mp3': cfg.get("sounds", "CMD_PLAY_MP3")
}


VOLUME = 50         # volume on a scale of 0-100.


def play(soundfile, blocking=BLOCKING):
    ext = soundfile.lower().strip()[-3:]

    if(ext in play_proc_map.keys()):
        proc = play_proc_map[ext]
    else:
        logger.fatal("Unrecognized file format: '" + ext.upper()+"'")
        return False

    logger.debug(proc + soundfile + ("" if blocking == BLOCKING else " &"))

    loc = os.path.dirname(os.path.realpath(__file__))
    cmd = proc.format(soundfile, ("" if blocking == BLOCKING else " &"))
    # cmd = proc + " " + soundfile + ("" if blocking == BLOCKING else " &")
    # logger.debug(cmd)
    # probably doesn't escape weird path characters, spaces, etc. properly
    p = subprocess.call(cmd, shell=True, cwd=loc)

    return p


def mute(state=True):
    """
        Mute / unmute sounds. NOTE: This controls Master volume. All audio
        sources will be affected.
    """
    return volume(0)


def volume(pcnt):
    """
        This controls Master volume. All audio
        sources will be affected.
        :param pcnt - Percent volume to set, as an integer
        between 1-100.
    """

    p = helper.map(pcnt, 0, 100, VOLUME_SCALE_MIN, VOLUME_SCALE_MAX)
    proc = cfg.get("sounds", "CMD_VOLUME").format(p)

    p = subprocess.call(proc, shell=True)

    return p


# mute(False)
volume(VOLUME)  # initialize volume

if (__name__ == "__main__"):
    while(True):
        logger.info("===PLAY (MP3, Volume 90%)===\n")
        volume(90)
        play("media/test.mp3", True)
        logger.info("returned\n")
        time.sleep(1.5)

        logger.info("===PLAY (WAV, MUTE)===\n")
        mute()
        play("media/portal/GLaDOS_init_surprise.wav", True)
        logger.info("returned\n")
        time.sleep(1.5)

        logger.info("===PLAY (WAV, UNMUTE)===\n")
        mute(False)
        play("media/portal/GLaDOS_init_surprise.wav", True)
        logger.info("returned\n")
        time.sleep(1.5)

        logger.info("===PLAY (WAV, Volume 70%)===\n")
        volume(70)
        play("media/portal/GLaDOS_init_surprise.wav", True)
        logger.info("returned\n")
        time.sleep(1.5)

        logger.info("===PLAY (WAV, Volume 80%)===\n")
        volume(80)
        play("media/portal/GLaDOS_init_surprise.wav", True)
        logger.info("returned\n")
        time.sleep(1.5)
