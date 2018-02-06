# cerberus
 Cerberus is an autonomous paintball sentry platform, powered by OpenCV on Raspberry Pi.

## General Algorithm
    * Use OpenCV frame-to-frame comparison to determine if there is a target in the frame. Also look for the disable signal (stop sign, specific t-shirt logo, etc).
    * Given the coordinates in the image of the thing we want to hit. translate that into servo commands, and move the servos to "aim".
    * Pull the trigger.
    * GOTO 10

## Future Improvements
    * Add a speaker to produce audible warning beeps.
    * Use laser pointer to auto-correct aiming / target leading.
    * Use a PID loop or Kalman filter (or something else?) to auto-correct targeting.
    * Add controls for windage and elevation.
    * Stereo cameras, for target distance estimation and auto-elevation correction

#Components
    * [Raspberry PI 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/), running Raspbian Stretch
    * [Adafruit Servo Hat](https://www.adafruit.com/product/2327)
    * [Castle creations 10A BEC](http://www.castlecreations.com/en/cc-bec-010-0004-00)
    * 2x [Hitec HS-5625MG servos](http://hitecrcd.com/products/servos/sport-servos/digital-sport-servos/hs-5625mg-high-speed-metal-gear-servo/product)
    * ServoCity Pan-tilt kit:
        * [SPT200 Pan & Tilt Kit](https://www.servocity.com/spt200) (24-tooth spline)
        * [Direct Drive Pan Mount](https://www.servocity.com/ddp-bm)
        * [1/4"-20 Round Screw Plate](https://www.servocity.com/0-250-20-round-screw-plate)
    * [Pi Camera board](https://www.adafruit.com/product/3099)
    * [Tripod](https://www.amazon.com/dp/B005KP473Q)
    * Enclosure: I used this [Pelican 1040 case](https://www.amazon.com/dp/B002E9GQEE), and mounted it to the front of the tripod platform using an L-bracket.
    * Battery: I used [this 2S LiPo](https://hobbyking.com/en_us/turnigy-nano-tech-ultimate-4600mah-2s2p-90c-hardcase-lipo-short-pack-roar-brca-approved.html). This battery is probably overkill for this project, but I liked it because it was the right dimensions to fit into the enclosure I chose, the right voltage to drive the regulator to 5V / 10A, and it has capacity and discharge rate to spare.
    * Paintball gun, with an "E-Trigger". I used the SmartParts Ion, which you can get for pretty cheap on eBay. I mounted the CO2 tank on one of the tripod legs, and used a hose to connect it to the actual gun. This removes some of the rotating mass from the gimbal setup, putting less strain on the motors, and making the gun easier to balance. I recommend this approach. otherwise, as the CO2 is used up, the center of mass will shift towards the front of the gun, unbalancing the platform, or throwing off your aim.
    * (Optional) Laser-dot sight. I used [this](https://www.amazon.com/dp/B01ITK4PEO), since I can "fire" it by pulling a GPIO pin LOW.
    * (Optional) Power Switch. I used [this](https://www.amazon.com/dp/B011DRFRVA), and followed [this tutorial](http://www.barryhubbard.com/raspberry-pi/howto-raspberry-pi-raspbian-power-on-off-gpio-button/) to set it up. Make sure you mount this in a place where you can reach it while the gun is armed, without getting shot in the face.
    * (Optional) Speaker, for making fun, Team-Fortress-inspired sentry gun noises. I used:
        * This [speaker](https://www.adafruit.com/product/1674), mounted to the inside of the enclosure.
        * This [amplifier](https://www.adafruit.com/product/2130), for driving the speaker from the RPi's underpowered audio jack.
