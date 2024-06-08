import { observer } from "mobx-react-lite"
import { ChangeEvent, FC } from "react"
import { useLocalization } from "../../../common/localize/useLocalization"
import { emptySong } from "../../../common/song"
import { Localized } from "../../../components/Localized"
import { MenuDivider, MenuItem } from "../../../components/Menu"
import { openSong, saveSong, setSong } from "../../actions"
import { createSong, updateSong } from "../../actions/cloudSong"
import { hasFSAccess, openFile, saveFileAs } from "../../actions/file"
import { useDialog } from "../../hooks/useDialog"
import { usePrompt } from "../../hooks/usePrompt"
import { useStores } from "../../hooks/useStores"
import { useToast } from "../../hooks/useToast"
import { FileInput } from "./LegacyFileMenu"

export const CloudFileMenu: FC<{ close: () => void }> = observer(
  ({ close }) => {
    const rootStore = useStores()
    const { rootViewStore, song } = rootStore
    const toast = useToast()
    const prompt = usePrompt()
    const dialog = useDialog()
    const localized = useLocalization()
    const isCloudSaved = song.cloudSongId !== null

    const saveOrCreateSong = async () => {
      const { song } = rootStore
      if (song.cloudSongId !== null) {
        if (song.name.length === 0) {
          const text = await prompt.show({
            title: localized("save-as", "Save as"),
          })
          if (text !== null && text.length > 0) {
            song.name = text
          }
        }
        await updateSong(rootStore)(song)
        toast.success(localized("song-saved", "Song saved"))
      } else {
        if (song.name.length === 0) {
          const text = await prompt.show({
            title: localized("save-as", "Save as"),
          })
          if (text !== null && text.length > 0) {
            song.name = text
          }
        }
        await createSong(rootStore)(song)
        toast.success(localized("song-created", "Song created"))
      }
    }

    // true: saved or not necessary
    // false: canceled
    const saveIfNeeded = async (): Promise<boolean> => {
      const { song } = rootStore
      if (song.isSaved) {
        return true
      }

      const res = await dialog.show({
        title: localized(
          "save-changes",
          "Do you want to save your changes to the song?",
        ),
        actions: [
          { title: localized("yes", "Yes"), key: "yes" },
          { title: localized("no", "No"), key: "no" },
          { title: localized("cancel", "Cancel"), key: "cancel" },
        ],
      })
      switch (res) {
        case "yes":
          await saveOrCreateSong()
          return true
        case "no":
          return true
        case "cancel":
          return false
      }
    }

    const onClickNew = async () => {
      close()
      try {
        if (!(await saveIfNeeded())) {
          return
        }
        const newSong = emptySong()
        setSong(rootStore)(newSong)
        await createSong(rootStore)(newSong)
        toast.success(localized("song-created", "Song created"))
      } catch (e) {
        toast.error((e as Error).message)
      }
    }

    const onClickOpen = async () => {
      close()
      try {
        if (!(await saveIfNeeded())) {
          return
        }
        rootViewStore.openCloudFileDialog = true
      } catch (e) {
        toast.error((e as Error).message)
      }
    }

    const onClickSave = async () => {
      close()
      try {
        await saveOrCreateSong()
      } catch (e) {
        toast.error((e as Error).message)
      }
    }

    const onClickSaveAs = async () => {
      const { song } = rootStore
      close()
      try {
        const text = await prompt.show({
          title: localized("save-as", "Save as"),
          initialText: song.name,
        })
        if (text !== null && text.length > 0) {
          song.name = text
        } else {
          return
        }
        await createSong(rootStore)(song)
        toast.success(localized("song-saved", "Song saved"))
      } catch (e) {
        toast.error((e as Error).message)
      }
    }

    const onClickRename = async () => {
      close()
      const { song } = rootStore
      try {
        const text = await prompt.show({
          title: localized("rename", "Rename"),
        })
        if (text !== null && text.length > 0) {
          song.name = text
        } else {
          return Promise.resolve(false)
        }
        if (song.cloudSongId !== null) {
          await updateSong(rootStore)(song)
        } else {
          await createSong(rootStore)(song)
        }
        toast.success(localized("song-saved", "Song saved"))
      } catch (e) {
        toast.error((e as Error).message)
      }
    }

    const onClickImportLegacy = async (e: ChangeEvent<HTMLInputElement>) => {
      close()
      try {
        await openSong(rootStore)(e.currentTarget)
        await saveOrCreateSong()
      } catch (e) {
        toast.error((e as Error).message)
      }
    }

    const onClickImport = async () => {
      close()
      try {
        if (!(await saveIfNeeded())) {
          return
        }
        await openFile(rootStore)
        await saveOrCreateSong()
      } catch (e) {
        toast.error((e as Error).message)
      }
    }

    const onClickExport = async () => {
      try {
        if (hasFSAccess) {
          await saveFileAs(rootStore)
        } else {
          saveSong(rootStore)()
        }
      } catch (e) {
        toast.error((e as Error).message)
      }
    }

    const onClickPublish = async () => {
      close()
      const { rootViewStore } = rootStore
      rootViewStore.openPublishDialog = true
    }

    return (
      <>
        <MenuItem onClick={onClickNew}>
          <Localized default="New">new-song</Localized>
        </MenuItem>

        <MenuDivider />

        <MenuItem onClick={onClickOpen}>
          <Localized default="Open">open-song</Localized>
        </MenuItem>

        <MenuItem onClick={onClickSave} disabled={rootStore.song.isSaved}>
          <Localized default="Save">save-song</Localized>
        </MenuItem>

        <MenuItem onClick={onClickSaveAs} disabled={!isCloudSaved}>
          <Localized default="Save As">save-as</Localized>
        </MenuItem>

        <MenuItem onClick={onClickRename} disabled={!isCloudSaved}>
          <Localized default="Rename">rename</Localized>
        </MenuItem>

        <MenuDivider />

        {!hasFSAccess && (
          <FileInput onChange={onClickImportLegacy}>
            <MenuItem>
              <Localized default="Import MIDI file">import-midi</Localized>
            </MenuItem>
          </FileInput>
        )}

        {hasFSAccess && (
          <MenuItem onClick={onClickImport}>
            <Localized default="Import MIDI file">import-midi</Localized>
          </MenuItem>
        )}

        <MenuItem onClick={onClickExport}>
          <Localized default="Export MIDI file">export-midi</Localized>
        </MenuItem>

        <MenuDivider />

        <MenuItem onClick={onClickPublish} disabled={!isCloudSaved}>
          <Localized default="Publish">publish</Localized>
        </MenuItem>
      </>
    )
  },
)
