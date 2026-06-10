import { Link } from "react-router-dom";
import type { SearchResult } from "../types";

export function SourceList({ sources }: { sources: SearchResult[] }) {
  if (sources.length === 0) {
    return (
      <div className="empty-state">
        <h3>目前還沒有可引用的筆記</h3>
        <p>先新增或補充筆記內容，再請 AI 依照筆記整理答案。</p>
      </div>
    );
  }

  return (
    <div className="source-list">
      {sources.map((source) => (
        <article key={`${source.noteId}-${source.chunkText.slice(0, 24)}`} className="source-card">
          <div className="source-card__header">
            <h3>{source.noteTitle}</h3>
            <span>{source.similarityScore.toFixed(2)}</span>
          </div>
          <p>{source.chunkText}</p>
          <Link to={`/notes/${source.noteId}`} className="text-link">
            檢視筆記
          </Link>
        </article>
      ))}
    </div>
  );
}
