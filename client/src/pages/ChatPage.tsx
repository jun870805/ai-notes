import { useState } from "react";
import { SourceList } from "../components/SourceList";
import { useNotesStore } from "../App";

export function ChatPage() {
  const { askNotes } = useNotesStore();
  const [question, setQuestion] = useState("我的筆記裡有提到 FastAPI 的 token 驗證怎麼做嗎？");

  const response = askNotes(question);

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <h2>AI 對話</h2>
        </div>
      </div>

      <section className="panel">
        <label className="field">
          <span>問題</span>
          <textarea value={question} onChange={(event) => setQuestion(event.target.value)} />
        </label>
      </section>

      <section className="answer-card">
        <div className="panel__heading">
          <h3>回答</h3>
          <span>附引用來源的 AI 回答</span>
        </div>
        <p>{response.answer}</p>
      </section>

      <section>
        <div className="panel__heading panel__heading--spaced">
          <h3>來源</h3>
          <span>本次引用的筆記片段</span>
        </div>
        <SourceList sources={response.sources} />
      </section>
    </section>
  );
}
