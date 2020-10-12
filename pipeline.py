import cv2
import numpy as np


class Pipeline:

    def crop(self, img, x, y, dx, dy):
        img_crop = img[y:(dy + 1), x:(dx + 1)]
        return img_crop


    def background_subtract(self, frame, first_frame):
        height, width = frame.shape[:2]
        first_frame = cv2.resize(first_frame, (width, height), interpolation=cv2.INTER_AREA)
        subt = cv2.absdiff(first_frame, frame)
        return subt


    def binarize(self, img, r, g, b, k):
        bin_img = np.zeros(img.shape, dtype=np.uint8)
        # getting height and width
        h = img.shape[0]
        w = img.shape[1]
        # looping through pixels and thresholding according to rgb value
        for y in range(0, h):
            for x in range(0, w):
                if (img[y, x, 2] * r
                    + img[y, x, 1] * g
                    + img[y, x, 0] * b >= k):
                    bin_img[y, x] = 255
        return bin_img


    def return_bytes(self, img):
        return cv2.imencode('.jpg', img)[1].tobytes()

