import os
import cv2
import csv
import numpy as np
import time
import peakutils
import logging
import matplotlib.pyplot as plt
from PIL import Image
from typing import Optional, List, Dict

logging.basicConfig(
    filename='keyframe_detection.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def scale(img, xScale, yScale):
    res = cv2.resize(img, None, fx=xScale, fy=yScale, interpolation=cv2.INTER_AREA)
    return res

def crop(infile, height, width):
    im = Image.open(infile)
    imgwidth, imgheight = im.size
    for i in range(imgheight // height):
        for j in range(imgwidth // width):
            box = (j * width, i * height, (j + 1) * width, (i + 1) * height)
            yield im.crop(box)

def averagePixels(path):
    r, g, b = 0, 0, 0
    count = 0
    pic = Image.open(path)
    for x in range(pic.size[0]):
        for y in range(pic.size[1]):
            imgData = pic.load()
            tempr, tempg, tempb = imgData[x, y]
            r += tempr
            g += tempg
            b += tempb
            count += 1
    return (r / count), (g / count), (b / count), count

def convert_frame_to_grayscale(frame):
    grayframe = None
    gray = None
    if frame is not None:
        cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = scale(gray, 1, 1)
        grayframe = scale(gray, 1, 1)
        gray = cv2.GaussianBlur(gray, (9, 9), 0.0)
    return grayframe, gray

def prepare_dirs(keyframePath, imageGridsPath, csvPath):
    if not os.path.exists(keyframePath):
        os.makedirs(keyframePath)
    if not os.path.exists(imageGridsPath):
        os.makedirs(imageGridsPath)
    if not os.path.exists(csvPath):
        os.makedirs(csvPath)


def plot_metrics(indices, lstfrm, lstdiffMag):
    y = np.array(lstdiffMag)
    plt.plot(indices, y[indices], "x")
    l = plt.plot(lstfrm, lstdiffMag, 'r-')
    plt.xlabel('frames')
    plt.ylabel('pixel difference')
    plt.title("Pixel value differences from frame to frame and the peak values")
    plt.show()

def keyframeDetection(source: str, Thres: float, max_keyframes: int = 10, plotMetrics: bool=False, verbose: bool=False, dest: Optional[str] = None):
    """
    A Key Frame is a location on a video timeline which marks the beginning or end of a smooth transition throughout the fotograms, 
    Key Frame Detector try to look for the most representative and significant frames that can describe the movement or main events in a video 
    using peakutils peak detection functions.
    """

    if dest is None:
        dest = source.split('.')[0]
    keyframePath = os.path.join(dest, 'keyFrames')
    imageGridsPath = os.path.join(dest, 'imageGrids')
    csvPath = os.path.join(dest, 'csvFile')
    path2file = os.path.join(csvPath, 'output.csv')
    prepare_dirs(keyframePath, imageGridsPath, csvPath)

    cap = cv2.VideoCapture(source)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if not cap.isOpened():
        logging.error("Error opening video file")
        cap.release()
        return

    lstfrm = []
    lstdiffMag = []
    timeSpans = []
    images = []
    full_color = []
    lastFrame = None
    Start_time = time.process_time()

    for i in range(length):
        ret, frame = cap.read()
        logging.debug(f"Processing frame {i} of {length}")
        if not ret:
            logging.warning(f"Frame {i} could not be read. Stopping early.")
            break

        grayframe, blur_gray = convert_frame_to_grayscale(frame)
        frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
        lstfrm.append(frame_number)
        images.append(grayframe)
        full_color.append(frame)

        if frame_number == 0:
            lastFrame = blur_gray
            lstdiffMag.append(0)
            timeSpans.append(0)
            continue

        diff = cv2.subtract(blur_gray, lastFrame)
        diffMag = cv2.countNonZero(diff)
        lstdiffMag.append(diffMag)

        stop_time = time.process_time()
        timeSpans.append(stop_time - Start_time)
        lastFrame = blur_gray

    cap.release()

    if len(lstdiffMag) < 3:
        logging.warning("Not enough frames for peak detection.")
        return

    y = np.array(lstdiffMag)
    base = peakutils.baseline(y, 2)
    indices = peakutils.indexes(y - base, Thres, min_dist=1)

    if len(indices) > max_keyframes:
        ranked_indices = sorted(indices, key=lambda i: lstdiffMag[i], reverse=True)[:max_keyframes]
        indices = sorted(ranked_indices)

    if plotMetrics:
        plot_metrics(indices, lstfrm, lstdiffMag)

    cnt = 1
    write_header = not os.path.exists(path2file)

    for x in indices:
        cv2.imwrite(os.path.join(keyframePath, f'keyframe{cnt}.jpg'), full_color[x])
        log_message = f'keyframe {cnt} happened at {timeSpans[x]} sec.'
        if verbose:
            logging.info(log_message)
        with open(path2file, 'a', newline='') as csvFile:
            writer = csv.writer(csvFile)
            if write_header:
                writer.writerow(["Keyframe Log"])
                write_header = False
            writer.writerow([log_message])
        cnt += 1

    cv2.destroyAllWindows()

