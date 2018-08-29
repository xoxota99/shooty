from __future__ import division
from threading import Thread
import cv2
import time
import imutils
import logging
from config import cfg

logger = logging.getLogger(__name__)

CAMERA_FOV_MIN_X = cfg.getint("vision", "CAMERA_FOV_MIN_X")
CAMERA_FOV_MAX_X = cfg.getint("vision", "CAMERA_FOV_MAX_X")
CAMERA_FOV_MIN_Y = cfg.getint("vision", "CAMERA_FOV_MIN_Y")
CAMERA_FOV_MAX_Y = cfg.getint("vision", "CAMERA_FOV_MAX_Y")

CV2_WARMUP_FRAMES = cfg.getint("vision", "CV2_WARMUP_FRAMES")
CV2_THRESHOLD_MIN = cfg.getint("vision", "CV2_THRESHOLD_MIN")
CV2_DILATE_ITERATIONS = cfg.getint("vision", "CV2_DILATE_ITERATIONS")
CV2_CONTOUR_MIN = cfg.getint("vision", "CV2_CONTOUR_MIN")
CV2_FPS = cfg.getint("vision", "CV2_FPS")
CV2_FRAME_WIDTH = cfg.getint("vision", "CV2_FRAME_WIDTH")
CV2_FRAME_HEIGHT = cfg.getint("vision", "CV2_FRAME_HEIGHT")


class Target:
    x = 0
    y = 0
    w = 0
    h = 0
    friendly = True
    id = -1

    def __init__(self, id, x, y, w, h, friendly):
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.friendly = friendly


class VisionWorker(Thread):
    target = None
    paused = False
    stopped = False
    target_acquired_callback = None
    target_lost_callback = None
    camera_port = 0
    show_video = False

    def __init__(self,
                 target_acquired_callback=None,
                 target_lost_callback=None,
                 camera_port=0,
                 show_video=False):

        Thread.__init__(self)
        self.target_acquired_callback = target_acquired_callback
        self.target_lost_callback = target_lost_callback
        self.camera_port = camera_port
        self.show_video = show_video

    def run(self):
        self.paused = False
        self.stopped = False

        cap = cv2.VideoCapture(self.camera_port)

        if not cap.isOpened():
            logger.warn("cap.isOpened=FALSE. Exiting.")
            self.stopped = True
            cap.release()
            return

        cap.set(cv2.CAP_PROP_FPS, CV2_FPS)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CV2_FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CV2_FRAME_HEIGHT)

        # initialize the first frame in the video stream
        firstFrame = None
        tempFrame = None
        count = 0

        # loop over the frames of the video
        while not self.stopped:
            if not self.paused:
                # grab the current frame and initialize the occupied/unoccupied
                # text

                (grabbed, frame) = cap.read()

                # if the frame could not be grabbed, then we have reached the
                # end of the video
                if not grabbed:
                    logger.warn("camera capture FAILED. Exiting...")
                    self.stopped = True
                    break

                # resize the frame, convert it to grayscale, and blur it
                frame = imutils.resize(frame, width=500)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)

                # if the first frame is None, initialize it
                if firstFrame is None:
                    logger.info("Auto-calibration of Video in progress...")
                    if tempFrame is None:
                        tempFrame = gray
                        continue
                    else:
                        # delta since last frame
                        delta = cv2.absdiff(tempFrame, gray)
                        tempFrame = gray

                        # if the delta for any pixel > 5, color it
                        # full white (255).
                        tst = cv2.threshold(delta, CV2_THRESHOLD_MIN, 255,
                                            cv2.THRESH_BINARY)[1]

                        # dilate the thresholded image to fill in holes,
                        # then find contours on thresholded image
                        tst = cv2.dilate(tst, None,
                                         iterations=CV2_DILATE_ITERATIONS)

                        if count > CV2_WARMUP_FRAMES:
                            # if frame capture is all warmed up
                            logger.info("Done warming up.\n Waiting for "
                                        "motion.")
                            if not cv2.countNonZero(tst) > 0:
                                # This is the first frame.
                                firstFrame = gray
                            continue
                        else:
                            # keep warming up.
                            count += 1
                            continue

                # openCV wakeup is completed.

                # compute the absolute difference between the current frame and
                # first frame
                frameDelta = cv2.absdiff(firstFrame, gray)

                # if the delta for any pixel > 25, color it full white (255).
                thresh = cv2.threshold(frameDelta,
                                       CV2_THRESHOLD_MIN,
                                       255,
                                       cv2.THRESH_BINARY)[1]

                # dilate the thresholded image to fill in holes, then find
                # contours on thresholded image
                thresh = cv2.dilate(thresh, None,
                                    iterations=CV2_DILATE_ITERATIONS)

                c = VisionWorker.get_best_contour(thresh.copy(),
                                                  CV2_CONTOUR_MIN)

                if c is not None:
                    # compute the bounding box for the contour, draw it on
                    # the frame, and update the text
                    (x, y, w, h) = cv2.boundingRect(c)

                    # Also assign the bounding box to the 'target'.
                    if self.target is None:
                        self.target = Target(
                            id=int(round(time.time() * 1000)),
                            x=x,
                            y=y,
                            w=w,
                            h=h,
                            friendly=True
                        )
                    else:
                        (self.target.x, self.target.y,
                         self.target.w, self.target.h) = (x, y, w, h)

                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)

                    if self.target_acquired_callback is not None:
                        self.target_acquired_callback(self.target, frame)
                else:
                    self.target = None
                    if self.target_lost_callback is not None:
                        self.target_lost_callback(frame)

                # show the frame and record if the user presses a key
                if self.show_video:
                    cv2.imshow("Security Feed", frame)
                    key = cv2.waitKey(1) & 0xFF

                    # if the `q` key is pressed, break from the loop
                    if key == ord("q"):
                        break

        # cleanup the camera and close any open windows
        cap.release()
        cv2.destroyAllWindows()

    def pause(self, state=True):
        self.paused = state

    def stop(self):
        self.stopped = True

    @staticmethod
    def get_best_contour(imgmask, threshold):
        """
        look at an image, find all the contours, and return the area of the
        largest contour above the specified area threshold.
        """
        im, contours, hierarchy = cv2.findContours(imgmask, cv2.RETR_EXTERNAL,
                                                   cv2.CHAIN_APPROX_SIMPLE)
        best_area = threshold
        best_cnt = None
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > best_area:
                best_area = area
                best_cnt = cnt
        return best_cnt


if __name__ == "__main__":

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    def target_acquired_callback(target, frame):
        """By default, do nothing. Just output the video frame and move on."""
        out.write(frame)
        time.sleep(0.001)

    def target_lost_callback(target, frame):
        """By default, do nothing. Just output the video frame and move on."""
        out.write(frame)
        time.sleep(0.001)

    scanner = VisionWorker(target_acquired_callback=target_acquired_callback,
                           target_lost_callback=target_lost_callback)
    scanner.daemon = True
    scanner.start()

    while not scanner.stopped:
        val = input("Capturing. 'Q' to quit.: ")

        if(val.lower() == "q" or scanner.stopped):
            break
        else:
            logger.warn("Unrecognized command: '{0}'".format(val))

    logger.info("Stopping.")
    scanner.stop()
    out.release()
