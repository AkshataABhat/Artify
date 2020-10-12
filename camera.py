import cv2


face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
ds_factor = 0.6


class VideoCamera(object):
    def __init__(self):
        # capturing video
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        # releasing camera
        self.video.release()

    def get_frame(self):
        ret, frame = self.video.read()
        return frame


    def get_faces(self):
        ret, frame = self.video.read()

        # detect faces
        frame = cv2.resize(frame, None, fx=ds_factor, fy=ds_factor,
                           interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_rects = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in face_rects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            break

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
