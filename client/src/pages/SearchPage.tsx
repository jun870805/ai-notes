import { useState } from "react";
import { SourceList } from "../components/SourceList";
import { useNotesStore } from "../App";

export function SearchPage() {
  const { searchNotes } = useNotesStore();
  const [query, setQuery] = useState("我之前是怎麼把 pgvector 接進語意搜尋流程的？");

  const results = searchNotes(query);

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">AI 搜尋頁</p>
          <h2>AI 搜尋</h2>
        </div>
      </div>

      <section className="panel">
        <label className="field">
          <span>搜尋問題</span>
          <textarea
            className="search-input"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
      </section>

      <section className="answer-card">
        <div className="panel__heading">
          <h3>搜尋結果</h3>
          <span>依相似度排序，最多顯示五筆命中片段</span>
        </div>
        <p>
          {results.length > 0
            ? `目前找到 ${results.length} 筆相關結果。`
            : "目前沒有找到相關結果。"}
        </p>
      </section>

      <section>
        <div className="panel__heading panel__heading--spaced">
          <h3>來源</h3>
          <span>本次命中的筆記片段</span>
        </div>
        <SourceList sources={results} />
      </section>
    </section>
  );
}
