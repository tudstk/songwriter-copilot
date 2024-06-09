import styled from "@emotion/styled";
import { FC, useState } from "react";
import { Localized } from "../../../components/Localized";
import { Tooltip } from "../../../components/Tooltip";
import { ToolbarButton } from "./ToolbarButton";
import { getSong } from "../../actions";
import { useStores } from "../../hooks/useStores";
import { useToast } from "../../hooks/useToast";

const DarkInput = styled.input`
    background-color: #1e1f24;
    color: white;
    width: 3rem;
    height: 1rem;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 2rem;
    margin-right: 0.5rem;
    cursor: pointer;

    &:hover {
        background-color: #555;
    }
`;

const CloseButton = styled.button`
    background: none;
    border: none;
    color: white;
    font-size: 1rem;
    cursor: pointer;
    margin-left: 0.5rem;
    margin-right: 0.5rem;
    &:hover {
        color: gray;
    }
`;

const Label = styled.label`
    color: white;
    margin-right: 0.5rem;
`;

const Select = styled.select`
    background-color: #1e1f24;
    color: white;
    height: 2rem;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 999px;
    margin-right: 0.5rem;
    cursor: pointer;

    &:hover {
        background-color: #555;
    }
`;

const steps = [
  "Number of bars",
  "Number of notes",
  "Number of steps",
  "Pauses",
  "Key",
  "Scale",
  "Root",
  "Population size",
  "Fitness Choice"
];

export const GenerateMusicIdeaButton: FC = () => {
  const rootStore = useStores();
  const toast = useToast();
  const [barsNumber, setBarsNumber] = useState(4);
  const [notesNumber, setNotesNumber] = useState(0);
  const [stepsNumber, setStepsNumber] = useState(0);
  const [pauses, setPauses] = useState("no");
  const [key, setKey] = useState("C");
  const [scale, setScale] = useState("major");
  const [root, setRoot] = useState(1);
  const [populationSize, setPopulationSize] = useState(1);
  const [fitnessChoice, setFitnessChoice] = useState("automated");
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [keySignature, setKeySignature] = useState("");
  const [showOptions, setShowOptions] = useState(false);

  const handleInitialClick = () => {
    setShowOptions(true);
  };

  const handleCloseClick = () => {
    setShowOptions(false);
    setKeySignature("");
    setCurrentStep(0);
  };

  const handleClick = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    console.log('Button clicked');
    try {
      setLoading(true);
      const response = await fetch(`http://127.0.0.1:5000/get_midi_file?bars=${barsNumber}&notes=${notesNumber}&steps=${stepsNumber}&pauses=${pauses}&key=${key}&scale=${scale}&root=${root}&population=${populationSize}&fitness=${fitnessChoice}`);
      if (!response.ok) {
        throw new Error('Failed to fetch MIDI file');
      }
      const midiBlob = await response.blob();
      const keySignature = response.headers.get('key-signature') ?? '';
      setKeySignature(keySignature);

      const randomNumber = Math.floor(100000 + Math.random() * 900000);
      const filename = `custom-idea-${randomNumber}.mid`;
      const url = window.URL.createObjectURL(midiBlob);
      const file = new File([midiBlob], filename, { type: 'audio/midi' });
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      try {
        await getSong(rootStore)(file);
      } catch (e) {
        toast.error((e as Error).message);
      } finally {
        setLoading(false);
      }
    } catch (error) {
      console.error('Error opening MIDI file:', error);
      setLoading(false);
    }
  };

  const nextStep = () => {
    setCurrentStep(currentStep + 1);
  };

  const renderCurrentStep = () => {
    switch (steps[currentStep]) {
      case "Number of bars":
        return (
          <>
            <Label htmlFor="barsInput">Number of bars</Label>
            <DarkInput
              id="barsInput"
              type="number"
              min="1"
              max="32"
              value={barsNumber}
              onChange={(e) => setBarsNumber(parseInt(e.target.value, 10))}
            />
          </>
        );
      case "Number of notes":
        return (
          <>
            <Label htmlFor="notesInput">Number of notes</Label>
            <DarkInput
              id="notesInput"
              type="number"
              min="1"
              value={notesNumber}
              onChange={(e) => setNotesNumber(parseInt(e.target.value, 10))}
            />
          </>
        );
      case "Number of steps":
        return (
          <>
            <Label htmlFor="stepsInput">Number of steps</Label>
            <DarkInput
              id="stepsInput"
              type="number"
              min="1"
              value={stepsNumber}
              onChange={(e) => setStepsNumber(parseInt(e.target.value, 10))}
            />
          </>
        );
      case "Pauses":
        return (
          <>
            <Label htmlFor="pausesInput">Pauses</Label>
            <Select id="pausesInput" value={pauses} onChange={(e) => setPauses(e.target.value)}>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </Select>
          </>
        );
      case "Key":
        return (
          <>
            <Label htmlFor="keyInput">Key</Label>
            <Select id="keyInput" value={key} onChange={(e) => setKey(e.target.value)}>
              {["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"].map(k => (
                <option key={k} value={k}>{k}</option>
              ))}
            </Select>
          </>
        );
      case "Scale":
        return (
          <>
            <Label htmlFor="scaleInput">Scale</Label>
            <Select id="scaleInput" value={scale} onChange={(e) => setScale(e.target.value)}>
              {["major", "minor", "dorian", "phrygian", "lydian", "mixolydian", "majorBlues", "minorBlues"].map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </Select>
          </>
        );
      case "Root":
        return (
          <>
            <Label htmlFor="rootInput">Root</Label>
            <DarkInput
              id="rootInput"
              type="number"
              min="1"
              max="7"
              value={root}
              onChange={(e) => setRoot(parseInt(e.target.value, 10))}
            />
          </>
        );
      case "Population size":
        return (
          <>
            <Label htmlFor="populationInput">Population size</Label>
            <DarkInput
              id="populationInput"
              type="number"
              min="1"
              max="20"
              value={populationSize}
              onChange={(e) => setPopulationSize(parseInt(e.target.value, 10))}
            />
          </>
        );
      case "Fitness Choice":
        return (
          <>
            <Label htmlFor="fitnessInput">Fitness Choice</Label>
            <Select id="fitnessInput" value={fitnessChoice} onChange={(e) => setFitnessChoice(e.target.value)}>
              <option value="automated">Automated</option>
              <option value="rating based">Rating Based</option>
            </Select>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <Tooltip title={<Localized default="Auto-Scroll">auto-scroll</Localized>}>
      <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }}>
        {!showOptions && (
          <ToolbarButton onMouseDown={handleInitialClick}>
            Generate Custom Idea
          </ToolbarButton>
        )}
        {showOptions && (
          <>
            {!loading && renderCurrentStep()}
            {currentStep < steps.length - 1 ? (
              <ToolbarButton onMouseDown={nextStep}>Next</ToolbarButton>
            ) : (
              <ToolbarButton onMouseDown={handleClick}>
                {loading ? "Loading..." : "Generate"}
              </ToolbarButton>
            )}
            {keySignature && <span style={{ marginLeft: '0.5rem' }}>Key: {keySignature}</span>}
            <CloseButton onMouseDown={handleCloseClick}>×</CloseButton>
          </>
        )}
      </div>
    </Tooltip>
  );
};
