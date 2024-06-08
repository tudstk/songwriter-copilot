import styled from "@emotion/styled";
import { FC, useState } from "react"; // Import useState hook
import { Localized } from "../../../components/Localized";
import { Tooltip } from "../../../components/Tooltip";
import { ToolbarButton } from "./ToolbarButton";
import { getSong } from "../../actions";
import { useStores } from "../../hooks/useStores";
import { useToast } from "../../hooks/useToast";

const DarkSelect = styled.select`
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

export const GenerateSongButton: FC = () => {
  const rootStore = useStores();
  const toast = useToast();
  const [selectedGenre, setSelectedGenre] = useState("rock");
  const [loading, setLoading] = useState(false);
  const [keySignature, setKeySignature] = useState("");

  const handleClick = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    console.log('Button clicked');
    try {
      setLoading(true);
      const response = await fetch(`http://127.0.0.1:5000/get_midi_file?genre=${selectedGenre}`);
      if (!response.ok) {
        throw new Error('Failed to fetch MIDI file');
      }
      const midiBlob = await response.blob();
      const keySignature = response.headers.get('key-signature') ?? '';
      setKeySignature(keySignature);

      const randomNumber = Math.floor(100000 + Math.random() * 900000);
      const filename = `${selectedGenre}-${randomNumber}.mid`;
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

  const handleGenreChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedGenre(e.target.value);
  };

  return (
    <Tooltip title={<Localized default="Auto-Scroll">auto-scroll</Localized>}>
      <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }}>
        {!loading && (
          <DarkSelect value={selectedGenre} onChange={handleGenreChange}>
            <option value="rock">Rock</option>
            <option value="poprock">Pop-Rock</option>
            <option value="classical">Classical</option>
            <option value="trap">Trap</option>
            <option value="lofi">Lofi</option>
          </DarkSelect>
        )}
        <ToolbarButton onMouseDown={handleClick} >
          {loading ? "Loading..." : "Generate"}
        </ToolbarButton>
        {keySignature}
        {keySignature && <span style={{ marginLeft: '0.5rem' }}>Key: {keySignature}</span>}
      </div>
    </Tooltip>
  );
};
