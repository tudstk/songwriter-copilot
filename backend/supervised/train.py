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
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint


def get_notes():
    notes = []

    for file in glob.glob("classical/*.mid"):
        midi = converter.parse(file)

        print("Parsing %s" % file)

        parsing_notes = None

        try:
            s2 = instrument.partitionByInstrument(midi)
            parsing_notes = s2.parts[0].recurse()
        except:
            parsing_notes = midi.flat.notes

        for unit in parsing_notes:
            if isinstance(unit, note.Note):
                notes.append(str(unit.pitch))
            elif isinstance(unit, chord.Chord):
                notes.append('.'.join(str(n) for n in unit.normalOrder))

    with open('./classical_model/notes', 'wb') as filepath:
        pickle.dump(notes, filepath)

    print("Total notes:", len(notes))  # Add this line for debugging

    return notes


def prepare_sequences(notes, n_vocab):
    sequence_length = 100
    name_of_pitch = sorted(set(item for item in notes))
    note_to_int = dict((note, number) for number, note in enumerate(name_of_pitch))

    inputs_model = []
    output_model = []

    # create input sequences and the corresponding outputs
    for i in range(0, len(notes) - sequence_length, 1):
        sequence_in = notes[i:i + sequence_length]
        sequence_out = notes[i + sequence_length]
        inputs_model.append([note_to_int[char] for char in sequence_in])
        output_model.append(note_to_int[sequence_out])

    n_patterns = len(inputs_model)

    # reshape the input into a format compatible with LSTM layers
    inputs_model = numpy.reshape(inputs_model, (n_patterns, sequence_length, 1))
    # normalize input
    inputs_model = inputs_model / float(n_vocab)

    print("Number of input sequences:", n_patterns)
    print("Length of output_model:", len(output_model))  # Add this line for debugging

    if n_patterns == 0:
        print("Error: No input sequences generated!")
        return None, None  # Return None for both inputs and outputs if there are no sequences

    output_model = np_utils.to_categorical(output_model)

    return inputs_model, output_model


def create_network(inputs_model, n_vocab, weights_file=None):
    model = Sequential()
    model.add(LSTM(
        512,
        input_shape=(inputs_model.shape[1], inputs_model.shape[2]),
        recurrent_dropout=0.3,
        return_sequences=True
    ))
    model.add(LSTM(512, return_sequences=True, recurrent_dropout=0.3, ))
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

    if weights_file:
        model.load_weights(weights_file)

    return model


def train(model, inputs_model, output_model):
    filepath = "classical_model/weights-improvement-{epoch:02d}-{loss:.4f}-bigger.hdf5"
    checkpoint = ModelCheckpoint(
        filepath,
        monitor='loss',
        verbose=0,
        save_best_only=True,
        mode='min'
    )
    callbacks_list = [checkpoint]

    model.fit(inputs_model, output_model, epochs=200, batch_size=128, callbacks=callbacks_list)

def train_network():
    notes = get_notes()
    n_vocab = len(set(notes))
    inputs_model, output_model = prepare_sequences(notes, n_vocab)
    model = create_network(inputs_model, n_vocab)
    train(model, inputs_model, output_model)


train_network()
