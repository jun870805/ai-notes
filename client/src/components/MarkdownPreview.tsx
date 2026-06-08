import type { ReactNode } from "react";

function renderInline(text: string) {
  const parts = text.split(/(`[^`]+`)/g);

  return parts.map((part, index) =>
    part.startsWith("`") && part.endsWith("`") ? (
      <code key={`${part}-${index}`}>{part.slice(1, -1)}</code>
    ) : (
      <span key={`${part}-${index}`}>{part}</span>
    ),
  );
}

export function MarkdownPreview({ content }: { content: string }) {
  const lines = content.split("\n");
  const nodes: ReactNode[] = [];
  let listItems: string[] = [];
  let codeBlock: string[] = [];
  let insideCodeBlock = false;

  const flushList = () => {
    if (listItems.length === 0) {
      return;
    }

    nodes.push(
      <ul key={`list-${nodes.length}`}>
        {listItems.map((item, index) => (
          <li key={`${item}-${index}`}>{renderInline(item)}</li>
        ))}
      </ul>,
    );
    listItems = [];
  };

  const flushCodeBlock = () => {
    if (codeBlock.length === 0) {
      return;
    }

    nodes.push(
      <pre key={`code-${nodes.length}`}>
        <code>{codeBlock.join("\n")}</code>
      </pre>,
    );
    codeBlock = [];
  };

  lines.forEach((line, index) => {
    if (line.trim().startsWith("```")) {
      if (insideCodeBlock) {
        flushCodeBlock();
      } else {
        flushList();
      }
      insideCodeBlock = !insideCodeBlock;
      return;
    }

    if (insideCodeBlock) {
      codeBlock.push(line);
      return;
    }

    if (line.startsWith("- ")) {
      listItems.push(line.slice(2));
      return;
    }

    flushList();

    if (!line.trim()) {
      return;
    }

    if (line.startsWith("### ")) {
      nodes.push(<h3 key={`h3-${index}`}>{line.slice(4)}</h3>);
      return;
    }

    if (line.startsWith("## ")) {
      nodes.push(<h2 key={`h2-${index}`}>{line.slice(3)}</h2>);
      return;
    }

    if (line.startsWith("# ")) {
      nodes.push(<h1 key={`h1-${index}`}>{line.slice(2)}</h1>);
      return;
    }

    nodes.push(<p key={`p-${index}`}>{renderInline(line)}</p>);
  });

  flushList();
  flushCodeBlock();

  return <div className="markdown-preview">{nodes}</div>;
}
