# sudo apt install sox
import os
duration = 0.5  # second
freq = 880  # Hz
os.system('play --no-show-progress --null --channels 1 synth %s sine %f' %
          (duration, freq))
