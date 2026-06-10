import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { chatWithNotes, searchNotes as searchNotesApi } from "./api/ai";
import {
  createNote as createNoteApi,
  deleteNote as deleteNoteApi,
  listNotes,
  updateNote as updateNoteApi,
} from "./api/notes";
import { AppLayout } from "./components/AppLayout";
import { ChatPage } from "./pages/ChatPage";
import { NoteDetailPage } from "./pages/NoteDetailPage";
import { NoteEditorPage } from "./pages/NoteEditorPage";
import { NotesListPage } from "./pages/NotesListPage";
import { SearchPage } from "./pages/SearchPage";
import type { ChatResponse, Note, NoteDraft, SearchResult } from "./types";

type NotesStoreValue = {
  notes: Note[];
  isLoading: boolean;
  errorMessage: string | null;
  saveNote: (draft: NoteDraft) => Promise<Note>;
  deleteNote: (noteId: string) => Promise<void>;
  getNote: (noteId: string) => Note | undefined;
  searchNotes: (query: string) => Promise<SearchResult[]>;
  askNotes: (question: string) => Promise<ChatResponse>;
  refreshNotes: () => Promise<void>;
};

const NotesStoreContext = createContext<NotesStoreValue | null>(null);

function NotesStoreProvider() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const refreshNotes = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await listNotes();
      setNotes(response);
      setErrorMessage(null);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "無法載入筆記。");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshNotes();
  }, [refreshNotes]);

  const saveNote = useCallback(async (draft: NoteDraft) => {
    const title = draft.title.trim() || "未命名筆記";
    const trimmedContent = draft.content.trim();
    const tags = draft.tags.map((tag) => tag.trim().toLowerCase()).filter(Boolean);

    const payload = { ...draft, title, content: trimmedContent, tags };
    const saved = draft.id ? await updateNoteApi(draft.id, payload) : await createNoteApi(payload);

    setNotes((currentNotes) => {
      const existing = currentNotes.some((note) => note.id === saved.id);
      if (existing) {
        return currentNotes.map((note) => (note.id === saved.id ? saved : note));
      }
      return [saved, ...currentNotes];
    });
    setErrorMessage(null);
    return saved;
  }, []);

  const deleteNote = useCallback(async (noteId: string) => {
    await deleteNoteApi(noteId);
    setNotes((currentNotes) => currentNotes.filter((note) => note.id !== noteId));
    setErrorMessage(null);
  }, []);

  const getNote = useCallback((noteId: string) => {
    return notes.find((note) => note.id === noteId);
  }, [notes]);

  const searchNotes = useCallback(async (query: string) => {
    return searchNotesApi(query);
  }, []);

  const askNotes = useCallback(async (question: string) => {
    return chatWithNotes(question);
  }, []);

  const value: NotesStoreValue = useMemo(
    () => ({
      notes,
      isLoading,
      errorMessage,
      saveNote,
      deleteNote,
      getNote,
      searchNotes,
      askNotes,
      refreshNotes,
    }),
    [askNotes, deleteNote, errorMessage, getNote, isLoading, notes, refreshNotes, saveNote, searchNotes],
  );

  return (
    <NotesStoreContext.Provider value={value}>
      <AppLayout noteCount={notes.length}>
        <Routes>
          <Route path="/" element={<Navigate to="/notes" replace />} />
          <Route path="/notes" element={<NotesListPage />} />
          <Route path="/notes/new" element={<NoteEditorPage />} />
          <Route path="/notes/:noteId" element={<NoteDetailPage />} />
          <Route path="/notes/:noteId/edit" element={<NoteEditorPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/chat" element={<ChatPage />} />
        </Routes>
      </AppLayout>
    </NotesStoreContext.Provider>
  );
}

export function useNotesStore() {
  const context = useContext(NotesStoreContext);

  if (!context) {
    throw new Error("useNotesStore 必須在 NotesStoreProvider 內使用");
  }

  return context;
}

export default NotesStoreProvider;
