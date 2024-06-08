from flask import Flask, send_file, make_response, request, jsonify
from flask_cors import CORS
from gen import generate_music

app = Flask(__name__)
CORS(app)


@app.route('/get_midi_file', methods=['GET'])
def send_midi():
    genre = request.args.get('genre')
    file_path, key_signature = generate_music(genre)
    if file_path:
        with open(file_path, 'rb') as f:
            midi_content = f.read()
        response = make_response(send_file(file_path, as_attachment=True, mimetype='audio/midi'))
        response.headers['key-signature'] = key_signature
        return response
    else:
        return "Failed to generate MIDI file", 500


if __name__ == '__main__':
    app.run(debug=True)