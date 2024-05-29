import glob
import pickle
import numpy
from music21 import converter, instrument, note, chord
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import Activation
from keras.layers import BatchNormalization as BatchNorm
from music21 import instrument, note, stream, chord



def generate():
    with open('./classical_model/notes', 'rb') as filepath:
        notes = pickle.load(filepath)

    name_of_pitch = sorted(set(item for item in notes))
    n_vocab = len(set(notes))

    inputs_model, normalized_input = prepare_sequences(notes, name_of_pitch, n_vocab)
    model = create_network(normalized_input, n_vocab)
    prediction_output = generate_notes(model, inputs_model, name_of_pitch, n_vocab)
    create_midi(prediction_output)


def prepare_sequences(notes, name_of_pitch, n_vocab):
    note_to_int = dict((note, number) for number, note in enumerate(name_of_pitch))

    sequence_length = 100
    inputs_model = []
    output = []
    for i in range(0, len(notes) - sequence_length, 1):
        sequence_in = notes[i:i + sequence_length]
        sequence_out = notes[i + sequence_length]
        inputs_model.append([note_to_int[char] for char in sequence_in])
        output.append(note_to_int[sequence_out])

    n_patterns = len(inputs_model)

    normalized_input = numpy.reshape(inputs_model, (n_patterns, sequence_length, 1))
    normalized_input = normalized_input / float(n_vocab)

    return (inputs_model, normalized_input)


def create_network(inputs_model, n_vocab):
    model = Sequential()
    model.add(LSTM(
        512,
        input_shape=(inputs_model.shape[1], inputs_model.shape[2]),
        recurrent_dropout=0.3,
        return_sequences=True
    ))
    model.add(LSTM(512, return_sequences=True, recurrent_dropout=0.3,))
    model.add(LSTM(512))
    model.add(BatchNorm())
    model.add(Dropout(0.3))
    model.add(Dense(256))
    model.add(Activation('relu'))
    model.add(BatchNorm())
    model.add(Dropout(0.3))
    model.add(Dense(n_vocab))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')
    model.load_weights('E:/Last Semester/Licenta/NewStuff/TryingStuff/classical_model/weights-improvement-194-0.0737-bigger.hdf5')

    return model


def generate_notes(model, inputs_model, name_of_pitch, n_vocab):

    start = numpy.random.randint(0, len(inputs_model)-1)

    int_to_note = dict((number, note) for number, note in enumerate(name_of_pitch))

    pattern = inputs_model[start]
    prediction_output = []

    # generate 500 notes
    for note_index in range(500):
        prediction_input = numpy.reshape(pattern, (1, len(pattern), 1))
        prediction_input = prediction_input / float(n_vocab)

        prediction = model.predict(prediction_input, verbose=0)

        index = numpy.argmax(prediction)
        result = int_to_note[index]
        prediction_output.append(result)

        pattern.append(index)
        pattern = pattern[1:len(pattern)]

    return prediction_output

def create_midi(prediction_output):
    offset = 0
    output_notes = []

    for pattern in prediction_output:
        if ('.' in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split('.')
            notes = []
            for current_note in notes_in_chord:
                new_note = note.Note(int(current_note))
                new_note.storedInstrument = instrument.Piano()
                notes.append(new_note)
            new_chord = chord.Chord(notes)
            new_chord.offset = offset
            output_notes.append(new_chord)
        else:
            new_note = note.Note(pattern)
            new_note.offset = offset
            new_note.storedInstrument = instrument.Piano()
            output_notes.append(new_note)

        offset += 0.5

    midi_stream = stream.Stream(output_notes)

    midi_stream.write('midi', fp='33.mid')

generate()