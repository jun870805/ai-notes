import { Link } from "react-router-dom";
import { TagChip } from "../components/TagChip";
import { useNotesStore } from "../App";
import { formatDate } from "../utils/format";

export function NotesListPage() {
  const { notes } = useNotesStore();

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
            <Link to={`/notes/${note.id}`} className="text-link">
              開啟編輯器
            </Link>
          </article>
        ))}
      </div>
    </section>
  );
}
