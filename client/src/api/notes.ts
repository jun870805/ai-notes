import { apiClient } from "./client";
import type { Note, NoteDraft } from "../types";

type NoteApi = {
  id: string;
  title: string;
  content: string;
  tags?: string[] | null;
  created_at: string;
  updated_at: string;
};

function mapNote(note: NoteApi): Note {
  return {
    id: note.id,
    title: note.title,
    content: note.content,
    tags: note.tags ?? [],
    createdAt: note.created_at,
    updatedAt: note.updated_at,
  };
}

export async function listNotes() {
  const notes = await apiClient.get<NoteApi[]>("/notes");
  return notes.map(mapNote);
}

export async function getNote(noteId: string) {
  const note = await apiClient.get<NoteApi>(`/notes/${noteId}`);
  return mapNote(note);
}

export async function createNote(draft: NoteDraft) {
  const note = await apiClient.post<NoteApi>("/notes", {
    title: draft.title,
    content: draft.content,
    tags: draft.tags.length > 0 ? draft.tags : null,
  });
  return mapNote(note);
}

export async function updateNote(noteId: string, draft: NoteDraft) {
  const note = await apiClient.put<NoteApi>(`/notes/${noteId}`, {
    title: draft.title,
    content: draft.content,
    tags: draft.tags.length > 0 ? draft.tags : null,
  });
  return mapNote(note);
}

export async function deleteNote(noteId: string) {
  return apiClient.delete<string>(`/notes/${noteId}`);
}
