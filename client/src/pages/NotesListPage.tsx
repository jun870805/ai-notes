import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { TagChip } from "../components/TagChip";
import { useNotesStore } from "../App";
import { formatDate } from "../utils/format";

export function NotesListPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { notes, isLoading, errorMessage, deleteNote } = useNotesStore();
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [deletingNoteId, setDeletingNoteId] = useState<string | null>(null);

  useEffect(() => {
    const message = location.state?.toastMessage;
    if (!message) {
      return;
    }

    setToastMessage(message);
    navigate(location.pathname, { replace: true, state: null });
  }, [location.pathname, location.state, navigate]);

  useEffect(() => {
    if (!toastMessage) {
      return;
    }

    const timeoutId = window.setTimeout(() => {
      setToastMessage(null);
    }, 2200);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [toastMessage]);

  const handleDelete = async (noteId: string) => {
    try {
      setDeletingNoteId(noteId);
      setDeleteError(null);
      await deleteNote(noteId);
      setToastMessage("筆記已刪除。");
    } catch (error) {
      setDeleteError(error instanceof Error ? error.message : "無法刪除筆記。");
    } finally {
      setDeletingNoteId(null);
    }
  };

  if (isLoading) {
    return (
      <section className="page-grid">
        <div className="section-heading">
          <div>
            <h2>筆記列表</h2>
          </div>
          <Link to="/notes/new" className="button">
            新增筆記
          </Link>
        </div>
        <section className="panel">
          <p>正在載入筆記...</p>
        </section>
      </section>
    );
  }

  return (
    <section className="page-grid">
      {toastMessage ? <div className="toast">{toastMessage}</div> : null}

      <div className="section-heading">
        <div>
          <h2>筆記列表</h2>
        </div>
        <Link to="/notes/new" className="button">
          新增筆記
        </Link>
      </div>

      {errorMessage || deleteError ? (
        <section className="panel">
          <p>{errorMessage ?? deleteError}</p>
        </section>
      ) : null}

      <div className="notes-grid">
        {notes.map((note) => (
          <article key={note.id} className="note-card">
            <div className="note-card__meta">
              <span>更新於 {formatDate(note.updatedAt)}</span>
              <span>{note.content.split(/\s+/).filter(Boolean).length} 字</span>
            </div>
            <h3>{note.title}</h3>
            <p>{note.content.slice(0, 160)}...</p>
            <div className="tag-row">
              {note.tags.map((tag) => (
                <TagChip key={tag} tag={tag} />
              ))}
            </div>
            <div className="note-card__actions">
              <Link to={`/notes/${note.id}`} className="text-link">
                檢視筆記
              </Link>
              <Link to={`/notes/${note.id}/edit`} className="text-link">
                編輯筆記
              </Link>
              <button
                type="button"
                className="text-button"
                onClick={() => void handleDelete(note.id)}
                disabled={deletingNoteId === note.id}
              >
                {deletingNoteId === note.id ? "刪除中..." : "刪除筆記"}
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
