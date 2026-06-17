import type { FormEvent, KeyboardEvent } from "react";
import { useEffect, useState } from "react";
import { MarkdownPreview } from "../components/MarkdownPreview";
import { SourceList } from "../components/SourceList";
import { useNotesStore } from "../App";
import type { ChatResponse } from "../types";

export function ChatPage() {
  const { askNotes } = useNotesStore();
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");
  const [response, setResponse] = useState<ChatResponse>({ answer: "", sources: [] });
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!submittedQuestion) {
      setResponse({ answer: "", sources: [] });
      setErrorMessage(null);
      setIsLoading(false);
      return;
    }

    let active = true;

    async function runChat() {
      try {
        setIsLoading(true);
        const nextResponse = await askNotes(submittedQuestion);
        if (!active) {
          return;
        }
        setResponse(nextResponse);
        setErrorMessage(null);
      } catch (error) {
        if (!active) {
          return;
        }
        setErrorMessage(error instanceof Error ? error.message : "無法完成 AI 對話。");
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    void runChat();
    return () => {
      active = false;
    };
  }, [askNotes, submittedQuestion]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextQuestion = question.trim();
    if (!nextQuestion || nextQuestion === submittedQuestion) {
      return;
    }
    setSubmittedQuestion(nextQuestion);
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key !== "Enter" || event.isComposing) {
      return;
    }

    if ((event.metaKey || event.ctrlKey) && event.shiftKey) {
      return;
    }

    event.preventDefault();
    const nextQuestion = question.trim();
    if (!nextQuestion || nextQuestion === submittedQuestion || isLoading) {
      return;
    }
    setSubmittedQuestion(nextQuestion);
  };

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <h2>AI 對話</h2>
        </div>
      </div>

      <form className="panel search-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>問題</span>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="請輸入想詢問的內容"
            disabled={isLoading}
          />
        </label>
        <div className="button-row button-row--end">
          <button type="submit" className="button" disabled={isLoading || !question.trim()}>
            {isLoading ? "整理中..." : "送出問題"}
          </button>
        </div>
      </form>

      <section className="answer-card">
        <div className="panel__heading">
          <h3>回答</h3>
          <span>附引用來源的 AI 回答</span>
        </div>
        <div className="answer-card__body">
          <MarkdownPreview content={errorMessage ?? (isLoading ? "正在整理回答..." : response.answer)} />
        </div>
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
