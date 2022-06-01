from flask import Flask, request
from flask_cors import CORS
import os
import uuid
from main import recognize

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = './audios'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

recognizeMapper = {
    'fs': {
        'success': True,
        'gender': 'female',
        'emotion': 'sad'
    },
    'fh': {
        'success': True,
        'gender': 'female',
        'emotion': 'happy'
    },
    'ma': {
        'success': True,
        'gender': 'male',
        'emotion': 'angry'
    },
    'ms': {
        'success': True,
        'gender': 'male',
        'emotion': 'sad'
    },
    'mh': {
        'success': True,
        'gender': 'male',
        'emotion': 'happy'
    }
}

@app.route("/audio", methods=['POST'])
def audio():
    print(request.files)
    file = request.files['wavfile']
    hash_name = uuid.uuid4().hex + '.wav'
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], hash_name))
    return recognize(hash_name)

@app.route("/preprocessed", methods=['GET'])
def predefined():
    target = request.args.get("target")
    return recognizeMapper[target]

if __name__ == "__main__":
    app.run(port=15000, debug=True, host='0.0.0.0')
