import type { FormEvent, KeyboardEvent } from "react";
import { useEffect, useState } from "react";
import { SourceList } from "../components/SourceList";
import { useNotesStore } from "../App";
import type { SearchResult } from "../types";

export function SearchPage() {
  const { searchNotes } = useNotesStore();
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!submittedQuery) {
      setResults([]);
      setErrorMessage(null);
      setIsSearching(false);
      return;
    }

    let active = true;

    async function runSearch() {
      try {
        setIsSearching(true);
        const nextResults = await searchNotes(submittedQuery);
        if (!active) {
          return;
        }
        setResults(nextResults);
        setErrorMessage(null);
      } catch (error) {
        if (!active) {
          return;
        }
        setErrorMessage(error instanceof Error ? error.message : "無法完成搜尋。");
      } finally {
        if (active) {
          setIsSearching(false);
        }
      }
    }

    void runSearch();
    return () => {
      active = false;
    };
  }, [searchNotes, submittedQuery]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextQuery = query.trim();
    if (!nextQuery || nextQuery === submittedQuery) {
      return;
    }
    setSubmittedQuery(nextQuery);
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key !== "Enter" || event.isComposing) {
      return;
    }

    if ((event.metaKey || event.ctrlKey) && event.shiftKey) {
      return;
    }

    event.preventDefault();
    const nextQuery = query.trim();
    if (!nextQuery || nextQuery === submittedQuery || isSearching) {
      return;
    }
    setSubmittedQuery(nextQuery);
  };

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <h2>AI 搜尋</h2>
        </div>
      </div>

      <form className="panel search-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>搜尋問題</span>
          <textarea
            className="search-input"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="請輸入搜尋內容"
            disabled={isSearching}
          />
        </label>
        <div className="button-row button-row--end">
          <button type="submit" className="button" disabled={isSearching || !query.trim()}>
            {isSearching ? "搜尋中..." : "搜尋"}
          </button>
        </div>
      </form>

      <section className="answer-card">
        <div className="panel__heading">
          <h3>搜尋結果</h3>
          <span>依相似度排序，最多顯示五筆命中片段</span>
        </div>
        <p>
          {errorMessage
            ? errorMessage
            : isSearching
              ? "正在搜尋..."
              : results.length > 0
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
