import { createContext, useContext, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/AppLayout";
import { ChatPage } from "./pages/ChatPage";
import { NoteEditorPage } from "./pages/NoteEditorPage";
import { NotesListPage } from "./pages/NotesListPage";
import { SearchPage } from "./pages/SearchPage";
import { buildChatAnswer, buildSearchResults, initialNotes } from "./utils/mockData";
import type { ChatResponse, Note, NoteDraft, SearchResult } from "./types";

type NotesStoreValue = {
  notes: Note[];
  saveNote: (draft: NoteDraft) => Note;
  deleteNote: (noteId: string) => void;
  getNote: (noteId: string) => Note | undefined;
  searchNotes: (query: string) => SearchResult[];
  askNotes: (question: string) => ChatResponse;
};

const NotesStoreContext = createContext<NotesStoreValue | null>(null);

function createSlug(value: string) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "") || "untitled-note";
}

function createTags(content: string) {
  const lowered = content.toLowerCase();
  const candidates = [
    "fastapi",
    "react",
    "pgvector",
    "auth",
    "websocket",
    "testing",
    "docker",
    "retrieval",
    "markdown",
    "frontend",
    "backend",
  ];

  const matches = candidates.filter((tag) => lowered.includes(tag)).slice(0, 5);
  return matches.length > 0 ? matches : ["engineering-note"];
}

function NotesStoreProvider() {
  const [notes, setNotes] = useState<Note[]>(initialNotes);

  const value: NotesStoreValue = {
    notes,
    saveNote(draft) {
      const now = new Date().toISOString();
      const title = draft.title.trim() || "未命名筆記";
      const trimmedContent = draft.content.trim();
      const cleanTags = draft.tags
        .map((tag) => tag.trim().toLowerCase())
        .filter(Boolean);
      const tags = cleanTags.length > 0 ? cleanTags : createTags(`${title}\n${trimmedContent}`);

      let savedNote: Note;

      setNotes((currentNotes) => {
        const existing = currentNotes.find((note) => note.id === draft.id);

        if (existing) {
          savedNote = {
            ...existing,
            title,
            content: trimmedContent,
            tags,
            updatedAt: now,
          };

          return currentNotes.map((note) => (note.id === draft.id ? savedNote : note));
        }

        savedNote = {
          id: createSlug(`${title}-${now}`),
          title,
          content: trimmedContent,
          tags,
          createdAt: now,
          updatedAt: now,
        };

        return [savedNote, ...currentNotes];
      });

      return savedNote!;
    },
    deleteNote(noteId) {
      setNotes((currentNotes) => currentNotes.filter((note) => note.id !== noteId));
    },
    getNote(noteId) {
      return notes.find((note) => note.id === noteId);
    },
    searchNotes(query) {
      return buildSearchResults(notes, query);
    },
    askNotes(question) {
      const sources = buildSearchResults(notes, question).slice(0, 3);
      return buildChatAnswer(question, sources);
    },
  };

  return (
    <NotesStoreContext.Provider value={value}>
      <AppLayout noteCount={notes.length}>
        <Routes>
          <Route path="/" element={<Navigate to="/notes" replace />} />
          <Route path="/notes" element={<NotesListPage />} />
          <Route path="/notes/new" element={<NoteEditorPage />} />
          <Route path="/notes/:noteId" element={<NoteEditorPage />} />
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
