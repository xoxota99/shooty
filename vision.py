import cv2
# import the necessary packages
from skimage.measure import compare_ssim
import argparse
import imutils
import cv2


target = {
    'x': 0,
    'y': 0,
    'w': 0,
    'h': 0,
    'friendly': True
}


def acquire_target(callback=None, camera_port=0, show_video=False):
    """
    Acquire the target, and populate the target member.
    :param:
    :return True if a target was acquired. False otherwise.:
    """
    camera = cv2.VideoCapture(camera_port)

# initialize the first frame in the video stream
    firstFrame = None
    tempFrame = None
    count = 0

    # loop over the frames of the video
    while True:
        # grab the current frame and initialize the occupied/unoccupied
        # text

        (grabbed, frame) = camera.read()

        # if the frame could not be grabbed, then we have reached the end
        # of the video
        if not grabbed:
            break

        # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # if the first frame is None, initialize it
        if firstFrame is None:
            print("Auto-calibration of Video in progres...")
            if tempFrame is None:
                tempFrame = gray
                continue
            else:
                # delta since last frame
                delta = cv2.absdiff(tempFrame, gray)
                tempFrame = gray

                # if the delta for any pixel > 5, color it full white (255).
                tst = cv2.threshold(delta, 5, 255, cv2.THRESH_BINARY)[1]

                # dilate the thresholded image to fill in holes, then find
                # contours on thresholded image
                tst = cv2.dilate(tst, None, iterations=2)
                if count > 30:  # if more than 30 frames have passed
                    print("Done.\n Waiting for motion.")
                    if not cv2.countNonZero(tst) > 0:
                        firstFrame = gray
                    else:
                        continue
                else:
                    count += 1
                    continue

        # openCV wakeup is completed.

        # compute the absolute difference between the current frame and
        # first frame
        frameDelta = cv2.absdiff(firstFrame, gray)

        # if the delta for any pixel > 25, color it full white (255).
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)

        c = get_best_contour(thresh.copy(), 5000)

        if c is not None:
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)

            # Also assign the bounding box to the 'target'.
            (target.x, target.y, target.w, target.h) = (x, y, w, h)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if callback is not None:
                callback(c, frame)

        # show the frame and record if the user presses a key
        if show_video:
            cv2.imshow("Security Feed", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key is pressed, break from the loop
            if key == ord("q"):
                break

    # cleanup the camera and close any open windows
    camera.release()
    cv2.destroyAllWindows()


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
