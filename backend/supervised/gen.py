import pickle
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, BatchNormalization as BatchNorm
from music21 import instrument, note, stream, chord


def load_notes(file_path):
    with open(file_path, 'rb') as filepath:
        return pickle.load(filepath)


def get_unique_notes(notes):
    return sorted(set(notes))


def prepare_sequences(notes, unique_notes, sequence_length=100):
    note_to_int = {note: number for number, note in enumerate(unique_notes)}
    num_unique_notes = len(unique_notes)

    input_sequences = []
    output_notes = []
    for i in range(len(notes) - sequence_length):
        input_seq = notes[i:i + sequence_length]
        output_note = notes[i + sequence_length]
        input_sequences.append([note_to_int[note] for note in input_seq])
        output_notes.append(note_to_int[output_note])

    num_patterns = len(input_sequences)

    normalized_inputs = np.reshape(input_sequences, (num_patterns, sequence_length, 1))
    normalized_inputs = normalized_inputs / float(num_unique_notes)

    return input_sequences, normalized_inputs, num_unique_notes


def create_model(input_shape, num_unique_notes, genre):
    model = Sequential()
    model.add(LSTM(512, input_shape=input_shape, recurrent_dropout=0.3, return_sequences=True))
    model.add(LSTM(512, return_sequences=True, recurrent_dropout=0.3))
    model.add(LSTM(512))
    model.add(BatchNorm())
    model.add(Dropout(0.3))
    model.add(Dense(256, activation='relu'))
    model.add(BatchNorm())
    model.add(Dropout(0.3))
    model.add(Dense(num_unique_notes, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')
    model.load_weights(
        f'E:/Last Semester/Licenta/NewStuff/TryingStuff/trained_models/{genre}.hdf5')
    return model


def generate_notes(model, input_sequences, unique_notes, num_unique_notes, num_generate=500):
    int_to_note = {number: note for number, note in enumerate(unique_notes)}

    start_index = np.random.randint(0, len(input_sequences) - 1)
    pattern = input_sequences[start_index]
    prediction_output = []

    for _ in range(num_generate):
        prediction_input = np.reshape(pattern, (1, len(pattern), 1))
        prediction_input = prediction_input / float(num_unique_notes)

        prediction = model.predict(prediction_input, verbose=0)
        index = np.argmax(prediction)
        result = int_to_note[index]
        prediction_output.append(result)

        pattern.append(index)
        pattern = pattern[1:]

    return prediction_output


def create_midi(prediction_output, genre):
    offset = 0
    output_notes = []
    output_file = f'{genre}.mid'

    for pattern in prediction_output:
        if '.' in pattern or pattern.isdigit():
            notes_in_chord = pattern.split('.')
            chord_notes = [note.Note(int(n)) for n in notes_in_chord]
            for n in chord_notes:
                n.storedInstrument = instrument.Piano()
            new_chord = chord.Chord(chord_notes)
            new_chord.offset = offset
            output_notes.append(new_chord)
        else:
            new_note = note.Note(pattern)
            new_note.offset = offset
            new_note.storedInstrument = instrument.Piano()
            output_notes.append(new_note)

        offset += 0.5

    midi_stream = stream.Stream(output_notes)
    key_signature = midi_stream.analyze('key')
    key_signature_str = str(key_signature)
    print(f"Key of the generated melody: {key_signature_str}")

    file_path = f"generated_music/{output_file}"
    midi_stream.write('midi', fp=file_path)
    return file_path, key_signature_str


def generate_music(genre):
    print("Generating music...")
    notes = load_notes(f'./{genre}_model/notes')
    unique_notes = get_unique_notes(notes)
    input_sequences, normalized_inputs, num_unique_notes = prepare_sequences(notes, unique_notes)
    model = create_model((normalized_inputs.shape[1], normalized_inputs.shape[2]), num_unique_notes, genre)
    prediction_output = generate_notes(model, input_sequences, unique_notes, num_unique_notes)
    file_path, key_signature_str = create_midi(prediction_output, genre)
    return file_path, key_signature_str


if __name__ == "__main__":
    file_path, key_signature = generate_music('rock')
