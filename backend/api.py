from flask import Flask, send_file, make_response, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from supervised.gen import generate_music
from reinforcement.main import run_genetic_algorithm
from reinforcement.utils import save_genome_to_midi

app = Flask(__name__)
CORS(app)

# Define a global dictionary to store ratings temporarily
# Key: filename, Value: rating
ratings_dict = {}


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


@app.route('/get_genome', methods=['GET'])
def send_genome():
    scale = request.args.get('scale')
    key = request.args.get('key')
    genome_index = request.args.get('genome_index')
    population_index = request.args.get('generation_index')

    file_path = f"{folder}/{population_index}/{scale}-{key}-{genome_index}.mid"
    print(file_path)
    if file_path:
        with open(file_path, 'rb') as f:
            midi_content = f.read()
        response = make_response(send_file(file_path, as_attachment=True, mimetype='audio/midi'))
        return response
    else:
        return "Failed to generate MIDI file", 500

@app.route('/generate_custom_melody', methods=['POST'])
def generate_custom_melody():
    data = request.json
    bars = int(data.get('bars', 8))
    num_notes = int(data.get('num_notes', 4))
    num_steps = int(data.get('num_steps', 1))
    pauses = data.get('pauses', True)
    key = data.get('key', 'C')
    scale = data.get('scale', 'major')
    root = int(data.get('root', 4))
    population_size = int(data.get('population_size', 3))
    fitness_choice = data.get('fitness_choice', 'rating')
    initial_rating = int(data.get('rating', 0))

    global ratings_dict, folder
    ratings_dict = {}
    folder = str(int(datetime.now().timestamp()))
    os.makedirs(folder, exist_ok=True)
    for population_id, population, next_generation, population_fitness in run_genetic_algorithm(
            bars, num_notes, num_steps, pauses, key, scale, root, population_size, fitness_choice, initial_rating
    ):
        for i, genome in enumerate(population):
            filename = f"{folder}/{scale}-{key}-{i}.mid"
            save_genome_to_midi(filename, genome, bars, num_notes, num_steps, pauses, key, scale, root, 120)

            # Store initial rating (0) for each generated MIDI file
            ratings_dict[filename] = initial_rating

    midi_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.mid')]
    print(ratings_dict)
    return jsonify(midi_files)


@app.route('/download_midi/<path:filename>', methods=['GET'])
def download_midi(filename):
    return send_file(filename, as_attachment=True)


@app.route('/rate_melody', methods=['POST'])
def rate_melody():
    try:
        data = request.json
        filename = data.get('filename')
        rating = int(data.get('rating'))

        # Update the rating for the specified filename
        ratings_dict[filename] = rating

        print(f"Melody {filename}: Rating: {rating}")
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
