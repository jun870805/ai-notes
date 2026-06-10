import { Link, useParams } from "react-router-dom";
import { MarkdownPreview } from "../components/MarkdownPreview";
import { TagChip } from "../components/TagChip";
import { useNotesStore } from "../App";
import { formatDate } from "../utils/format";

export function NoteDetailPage() {
  const { noteId } = useParams();
  const { getNote, isLoading } = useNotesStore();
  const selectedNote = noteId ? getNote(noteId) : undefined;

  if (noteId && isLoading) {
    return (
      <section className="page-grid">
        <div className="section-heading">
          <div>
            <h2>檢視筆記</h2>
          </div>
        </div>
        <section className="panel">
          <p>正在載入筆記...</p>
        </section>
      </section>
    );
  }

  if (noteId && !selectedNote) {
    return (
      <section className="page-grid">
        <div className="section-heading">
          <div>
            <h2>檢視筆記</h2>
          </div>
          <Link to="/notes" className="button button--quiet">
            返回筆記列表
          </Link>
        </div>
        <section className="panel">
          <p>找不到這篇筆記。</p>
        </section>
      </section>
    );
  }

  if (!selectedNote) {
    return null;
  }

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <h2>檢視筆記</h2>
        </div>
        <div className="button-row">
          <Link to={`/notes/${selectedNote.id}/edit`} className="button">
            編輯筆記
          </Link>
          <Link to="/notes" className="button button--quiet">
            返回筆記列表
          </Link>
        </div>
      </div>

      <section className="panel detail-stack">
        <div className="panel__heading panel__heading--spaced">
          <h3>{selectedNote.title}</h3>
          <span>
            更新於 {formatDate(selectedNote.updatedAt)} · {selectedNote.content.split(/\s+/).filter(Boolean).length} 字
          </span>
        </div>

        {selectedNote.tags.length > 0 ? (
          <div className="tag-row">
            {selectedNote.tags.map((tag) => (
              <TagChip key={tag} tag={tag} />
            ))}
          </div>
        ) : null}

        <div className="detail-divider" />
        <MarkdownPreview content={selectedNote.content} />
      </section>
    </section>
  );
}
