import logging
from flask import Flask, send_file, make_response, request, jsonify
from flask_cors import CORS
from datetime import datetime
from supervised.gen import generate_music
from reinforcement.utils import save_genome_to_midi
from reinforcement.genetic_algorithm import fitness_automated, run_evolution
from pyo import *
import os

os.environ['PYTHONUNBUFFERED'] = '1'

app = Flask(__name__)
CORS(app)

DEFAULT_NUM_MUTATIONS = 2
DEFAULT_MUTATION_PROBABILITY = 0.5
DEFAULT_BPM = 120
BITS_PER_NOTE = 4

ratings = {}


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


@app.route('/get_best_genome', methods=['GET'])
def send_best_genome():
    population_index = request.args.get('generation_index')
    file_path = f"{folder}/{population_index}/best.mid"
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
    population_size = int(data.get('population_size', 4))
    number_of_generations = data.get('number_of_generations')
    print("population size:", population_size)
    fitness_choice = data.get('fitness_choice')
    print(fitness_choice)

    global folder
    num_mutations = DEFAULT_NUM_MUTATIONS
    mutation_probability = DEFAULT_MUTATION_PROBABILITY
    bpm = DEFAULT_BPM
    fitness_func = fitness_automated if fitness_choice == 'Automated' else fitness_rating_mode

    best_genome = None
    best_fitness = float('-inf')
    previous_best_genome = None
    previous_best_fitness = None
    folder = str(int(datetime.now().timestamp()))
    os.makedirs(folder, exist_ok=True)
    genome_length = bars * num_notes * BITS_PER_NOTE
    s = Server().boot()

    generation_index = 0

    for population_id, population, next_generation, population_fitness in run_evolution(
            population_size, genome_length, fitness_func, num_mutations, mutation_probability,
            bars, num_notes, num_steps, pauses, key, scale, root
    ):
        print(f"Population {population_id} done")

        print("Saving results...")
        sorted_population = sorted(population_fitness, key=lambda x: x[1], reverse=True)
        for i, (genome, fitness) in enumerate(sorted_population):
            save_genome_to_midi(f"{folder}/{population_id}/{scale}-{key}-{i}.mid", genome, bars, num_notes,
                                num_steps,
                                pauses, key, scale, root, bpm)

        new_best_genome = None
        new_best_fitness = float('-inf')
        for genome, fitness in sorted_population:
            if fitness != previous_best_fitness:
                new_best_genome = genome
                new_best_fitness = fitness
                break

        if new_best_genome is None:
            if len(sorted_population) > 1:
                new_best_genome = sorted_population[1][0]
                new_best_fitness = sorted_population[1][1]
            else:
                new_best_genome = sorted_population[0][0]
                new_best_fitness = sorted_population[0][1]

        best_genome = new_best_genome
        best_fitness = new_best_fitness
        previous_best_genome = best_genome
        previous_best_fitness = best_fitness

        if best_genome is not None:
            save_genome_to_midi(f"{folder}/{population_id}/best.mid", best_genome, bars, num_notes,
                                num_steps, pauses, key, scale,
                                root, bpm)
        print("Done!")

        if generation_index >= number_of_generations:
            return jsonify({'success': True})
        else:
            generation_index += 1


def fitness_rating_mode(genome, bars, num_notes, num_steps, pauses, key, scale, root):
    if ratings:
        min_key = min(ratings.keys(), key=lambda x: int(x.split('-')[-1].split('.')[0]))
        min_value = ratings[min_key]
        del ratings[min_key]
        print(f"Smallest index key found: {min_key}")
        print(f"Corresponding value: {min_value}")
        return min_value
    else:
        print("Dictionary 'ratings' is empty.")
        return 0


@app.route('/rate_melody', methods=['POST'])
def rate_melody():
    try:
        data = request.json
        filename = data.get('filename')
        rating = int(data.get('rating'))
        print(f"Melody {filename}: Rating: {rating}")
        ratings[filename] = rating
        print(ratings)

        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error rating melody: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
