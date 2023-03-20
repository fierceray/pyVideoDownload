from flask import Flask, request, render_template, redirect, send_from_directory

from videoFile import VideoFile



application = Flask(__name__)

@application.route('/', methods=["POST", "GET"])
def index():
    if request.method == 'POST':
        url = request.form.get('input_url')
        print(url)
        videoFile = VideoFile(url)
        path, file = videoFile.execute()

    return send_from_directory(directory=path, filename=file)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    application.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
