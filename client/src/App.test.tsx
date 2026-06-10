import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderApp } from "./test/utils";
import { initialNotes } from "./utils/mockData";

function toApiNote(note: (typeof initialNotes)[number]) {
  return {
    id: note.id,
    title: note.title,
    content: note.content,
    tags: note.tags,
    created_at: note.createdAt,
    updated_at: note.updatedAt,
  };
}

function envelope(data: unknown, init?: { code?: string; success?: boolean; message?: string | null }) {
  return {
    code: init?.code ?? "success",
    success: init?.success ?? true,
    message: init?.message ?? null,
    data,
  };
}

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? "GET";

      if (url.endsWith("/api/v1/notes") && method === "GET") {
        return Response.json(envelope(initialNotes.map(toApiNote)));
      }

      if (url.endsWith("/api/v1/notes") && method === "POST") {
        const body = JSON.parse(String(init?.body));
        return Response.json(
          envelope({
            id: "created-note-id",
            title: body.title,
            content: body.content,
            tags: body.tags ?? [],
            created_at: "2026-06-10T00:00:00Z",
            updated_at: "2026-06-10T00:00:00Z",
          }),
          { status: 201 },
        );
      }

      if (url.includes("/api/v1/notes/") && method === "PUT") {
        const body = JSON.parse(String(init?.body));
        const noteId = url.split("/").pop();
        return Response.json(
          envelope({
            id: noteId,
            title: body.title,
            content: body.content,
            tags: body.tags ?? [],
            created_at: "2026-06-10T00:00:00Z",
            updated_at: "2026-06-10T00:00:00Z",
          }),
        );
      }

      if (url.includes("/api/v1/notes/") && method === "DELETE") {
        return Response.json(envelope("note deleted"));
      }

      if (url.endsWith("/api/v1/ai/search")) {
        return Response.json(
          envelope({
            results: [
              {
                note_id: initialNotes[1].id,
                note_title: initialNotes[1].title,
                chunk_text: "Enable vector extension in the database init script.",
                similarity_score: 0.91,
              },
            ],
          }),
        );
      }

      if (url.endsWith("/api/v1/ai/chat")) {
        return Response.json(
          envelope({
            answer: "根據目前檢索到的筆記內容，JWT middleware 會先驗證 bearer token。",
            sources: [
              {
                note_id: initialNotes[0].id,
                note_title: initialNotes[0].title,
                chunk_text: "JWT middleware 會在進入 route logic 前先驗證 bearer token。",
                similarity_score: 0.93,
              },
            ],
          }),
        );
      }

      return Response.json(envelope(null, { code: "not_mocked", success: false, message: `Unhandled ${method} ${url}` }), {
        status: 500,
      });
    }) as typeof fetch,
  );
});

describe("client app", () => {
  it("renders localized primary navigation and product title", async () => {
    renderApp("/notes");

    expect(await screen.findByRole("heading", { name: "AI 工程筆記" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "筆記" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "AI 搜尋" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "AI 對話" })).toBeInTheDocument();
  });

  it("shows a consistent three-section layout for AI 搜尋", async () => {
    renderApp("/search");

    expect(await screen.findByRole("heading", { name: "AI 搜尋" })).toBeInTheDocument();
    expect(screen.getByLabelText("搜尋問題")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "搜尋結果" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "來源" })).toBeInTheDocument();
  });

  it("shows a consistent three-section layout for AI 對話", async () => {
    renderApp("/chat");

    expect(await screen.findByRole("heading", { name: "AI 對話" })).toBeInTheDocument();
    expect(screen.getByLabelText("問題")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "回答" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "來源" })).toBeInTheDocument();
  });

  it("saves a new note and returns to the notes list with a success toast", async () => {
    const user = userEvent.setup();
    renderApp("/notes/new");

    await user.clear(screen.getByLabelText("標題"));
    await user.type(screen.getByLabelText("標題"), "新的測試筆記");
    await user.clear(screen.getByLabelText("Markdown 內容"));
    await user.type(screen.getByLabelText("Markdown 內容"), "# 測試內容");
    await user.click(screen.getByRole("button", { name: "儲存筆記" }));

    expect(await screen.findByRole("heading", { name: "筆記列表" })).toBeInTheDocument();
    expect(screen.getByText("筆記已儲存。")).toBeInTheDocument();
  });

  it("opens a note in preview mode before entering edit mode", async () => {
    const user = userEvent.setup();
    renderApp("/notes");

    await user.click(await screen.findByRole("link", { name: "檢視筆記" }));

    expect(await screen.findByRole("heading", { name: "檢視筆記" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "編輯筆記" })).toBeInTheDocument();
  });

  it("navigates between tabs without losing the active tab label", async () => {
    const user = userEvent.setup();
    renderApp("/notes");

    await user.click(screen.getByRole("link", { name: "AI 搜尋" }));
    expect(screen.getByRole("heading", { name: "AI 搜尋" })).toBeInTheDocument();

    await user.click(screen.getByRole("link", { name: "AI 對話" }));
    expect(screen.getByRole("heading", { name: "AI 對話" })).toBeInTheDocument();
  });
});
