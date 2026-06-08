import type { ChatResponse, Note, SearchResult } from "../types";

export const initialNotes: Note[] = [
  {
    id: "sample-fastapi-auth-notes",
    title: "範例筆記：FastAPI 驗證筆記",
    tags: ["fastapi", "auth", "backend", "jwt"],
    createdAt: "2026-05-20T09:00:00.000Z",
    updatedAt: "2026-05-27T08:15:00.000Z",
    content: `# FastAPI 驗證筆記

- JWT middleware 會在進入 route logic 前先驗證 bearer token。
- Token payload 內記錄 user id 與 session version。
- Refresh token rotation 需要撤銷舊的 token family。

## Debug 紀錄

本機測試時因為少了 clock skew 處理，導致短效 token 偶發驗證失敗。

\`\`\`python
def validate_token(token: str) -> bool:
    return token.startswith("ey")
\`\`\``,
  },
  {
    id: "sample-pgvector-setup-notes",
    title: "範例筆記：pgvector 建置筆記",
    tags: ["pgvector", "retrieval", "docker", "postgres"],
    createdAt: "2026-05-21T10:30:00.000Z",
    updatedAt: "2026-05-29T04:20:00.000Z",
    content: `# pgvector 建置筆記

- 在資料庫初始化腳本中啟用 vector extension。
- note chunks 需儲存 note_id、chunk_text、embedding 與 created_at。
- 搜尋結果依相似度排序，回傳 Top 5。

## Chunk 切分規則

每個 chunk 建議落在 500 到 800 tokens，並保留 50 到 100 tokens overlap，以維持檢索品質。`,
  },
  {
    id: "sample-react-markdown-notes",
    title: "範例筆記：React Markdown 預覽",
    tags: ["react", "markdown", "frontend", "preview"],
    createdAt: "2026-05-22T07:20:00.000Z",
    updatedAt: "2026-06-01T11:05:00.000Z",
    content: `# React Markdown 預覽

- 編輯器輸入狀態保留在 local state。
- 桌面版讓 preview 與 editor 並排，手機版改為上下堆疊。
- 預覽層避免直接渲染不安全的 HTML。

## 介面備註

使用者不離開頁面也要看得到 tags、儲存按鈕與刪除按鈕。`,
  },
];

function scoreText(text: string, query: string) {
  const haystack = text.toLowerCase();
  const terms = query
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter(Boolean);

  if (terms.length === 0) {
    return 0;
  }

  let score = 0;

  terms.forEach((term) => {
    if (haystack.includes(term)) {
      score += 1;
    }
  });

  return score / terms.length;
}

function excerptForQuery(content: string, query: string) {
  const sentences = content
    .replace(/\n+/g, " ")
    .split(/(?<=[.!?])\s+/)
    .filter(Boolean);
  const ranked = [...sentences].sort(
    (left, right) => scoreText(right, query) - scoreText(left, query),
  );

  return ranked[0] || content.slice(0, 180);
}

export function buildSearchResults(notes: Note[], query: string): SearchResult[] {
  return notes
    .map((note) => ({
      noteId: note.id,
      noteTitle: note.title,
      chunkText: excerptForQuery(note.content, query),
      similarityScore: Number((0.55 + scoreText(`${note.title} ${note.content}`, query) * 0.45).toFixed(2)),
    }))
    .filter((result) => result.similarityScore > 0.55)
    .sort((left, right) => right.similarityScore - left.similarityScore)
    .slice(0, 5);
}

export function buildChatAnswer(question: string, sources: SearchResult[]): ChatResponse {
  if (sources.length === 0) {
    return {
      answer:
        "目前筆記資料不足，還無法回答這個問題。請先新增筆記，或改問目前筆記中已經涵蓋的主題。",
      sources: [],
    };
  }

  const noteTitles = sources.map((source) => source.noteTitle.replace("範例筆記：", ""));

  return {
    answer: `根據 ${noteTitles.join("、")} 的內容，目前可以整理出：${sources
      .map((source) => source.chunkText)
      .join(" ")} 這段回答只根據本次檢索到、與問題「${question}」相關的筆記內容生成。`,
    sources,
  };
}
