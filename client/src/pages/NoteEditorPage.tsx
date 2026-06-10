import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { MarkdownPreview } from "../components/MarkdownPreview";
import { TagChip } from "../components/TagChip";
import { useNotesStore } from "../App";

export function NoteEditorPage() {
  const { noteId } = useParams();
  const navigate = useNavigate();
  const { getNote, saveNote, deleteNote, isLoading } = useNotesStore();
  const selectedNote = noteId ? getNote(noteId) : undefined;

  const [title, setTitle] = useState("");
  const [content, setContent] = useState(`# 摘要\n\n請用 Markdown 撰寫這篇筆記。\n`);
  const [tagsInput, setTagsInput] = useState("");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (!selectedNote) {
      setTitle("");
      setContent(`# 摘要\n\n請用 Markdown 撰寫這篇筆記。\n`);
      setTagsInput("");
      return;
    }

    setTitle(selectedNote.title);
    setContent(selectedNote.content);
    setTagsInput(selectedNote.tags.join(", "));
  }, [selectedNote]);

  const tagList = tagsInput
    .split(",")
    .map((tag) => tag.trim().toLowerCase())
    .filter(Boolean);

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setSubmitError(null);
      await saveNote({
        id: selectedNote?.id,
        title,
        content,
        tags: tagList,
      });
      navigate("/notes", {
        state: {
          toastMessage: "筆記已儲存。",
        },
      });
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "無法儲存筆記。");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedNote) {
      return;
    }

    try {
      setIsDeleting(true);
      setSubmitError(null);
      await deleteNote(selectedNote.id);
      navigate("/notes");
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "無法刪除筆記。");
    } finally {
      setIsDeleting(false);
    }
  };

  if (noteId && isLoading) {
    return (
      <section className="page-grid">
        <div className="section-heading">
          <div>
            <h2>編輯筆記</h2>
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
            <h2>編輯筆記</h2>
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

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <h2>{selectedNote ? "編輯筆記" : "新增筆記"}</h2>
        </div>
        <div className="button-row">
          <button type="button" className="button" onClick={() => void handleSave()} disabled={isSaving}>
            {isSaving ? "儲存中..." : "儲存筆記"}
          </button>
          {selectedNote ? (
            <button
              type="button"
              className="button button--quiet"
              onClick={() => void handleDelete()}
              disabled={isDeleting}
            >
              {isDeleting ? "刪除中..." : "刪除筆記"}
            </button>
          ) : (
            <Link to="/notes" className="button button--quiet">
              返回筆記列表
            </Link>
          )}
        </div>
      </div>
      {submitError ? (
        <section className="panel">
          <p>{submitError}</p>
        </section>
      ) : null}

      <div className="editor-layout">
        <section className="panel">
          <label className="field">
            <span>標題</span>
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="FastAPI 驗證筆記"
            />
          </label>

          <label className="field">
            <span>標籤</span>
            <input
              value={tagsInput}
              onChange={(event) => setTagsInput(event.target.value)}
              placeholder="fastapi, auth, backend"
            />
          </label>

          <div className="tag-row">
            {tagList.map((tag) => (
              <TagChip key={tag} tag={tag} />
            ))}
          </div>

          <label className="field">
            <span>Markdown 內容</span>
            <textarea value={content} onChange={(event) => setContent(event.target.value)} />
          </label>
        </section>

        <section className="panel panel--preview">
          <div className="panel__heading">
            <h3>預覽</h3>
            <span>Markdown 預覽</span>
          </div>
          <MarkdownPreview content={content} />
        </section>
      </div>
    </section>
  );
}
