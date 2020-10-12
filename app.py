from flask import Flask, render_template, Response, url_for, request, redirect, session
import json
from camera import VideoCamera
from pipeline import Pipeline


app = Flask(__name__)

app.config['SECRET_KEY'] = 'gust93x'


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html') #, form=form)


def gen(camera):
    while True:
        # get camera frame
        frame = camera.get_frame()
        output = Pipeline().return_bytes(frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + output + b'\r\n\r\n')


def gen_face_detection(camera):
    while True:
        frame = camera.get_faces()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def gen_stream_pipeline(camera, params):
    # get parameters from web
    crop_params_array = params["crop_params"].split(",")
    bin_params_array = params["bin_params"].split(",")

    for i in range(len(crop_params_array)):
        crop_params_array[i] = crop_params_array[i].strip()

    for i in range(len(bin_params_array)):
        bin_params_array[i] = bin_params_array[i].strip()

    x, y, dx, dy = crop_params_array[0], crop_params_array[1], crop_params_array[2], crop_params_array[3]
    r, g, b, k = bin_params_array[0], bin_params_array[1], bin_params_array[2], bin_params_array[3]

    first_frame = camera.get_frame()

    while True:
        # apply pipeline blocks
        frame = camera.get_frame()
        crop = Pipeline().crop(frame, int(x), int(y), int(dx), int(dy))
        bckgrnd_sub = Pipeline().background_subtract(crop, first_frame)
        first_frame = crop # update first frame for next iteration
        bin_img = Pipeline().binarize(bckgrnd_sub,
                                      int(r), int(g), int(b), int(k))
        output = Pipeline().return_bytes(bin_img)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + output + b'\r\n\r\n')


@app.route('/stream_feed')
def stream_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/pipeline_feed', methods=['GET', 'POST']) # in progress
def pipeline_feed():
    data = session['data']
    return Response(gen_stream_pipeline(VideoCamera(), data),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/faces_feed')
def faces_feed():
    return Response(gen_face_detection(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/handle_data', methods=['POST'])
def handle_data():
    data = request.get_json()
    session['data'] = data
    return json.dumps({"success": True, "data": data})


if __name__ == '__main__':
    app.run(debug=True)