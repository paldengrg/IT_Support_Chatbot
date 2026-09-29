function renderInline(text) {
  return text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).map((part, i) => {
    if (part.length > 2 && part.startsWith("`") && part.endsWith("`")) {
      return <code key={i}>{part.slice(1, -1)}</code>;
    }
    if (part.length > 4 && part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

// Minimal markdown: paragraphs, numbered lists, bullet lists, `code`, **bold**.
// Blank lines do not end a list, so "1. ...\n\n2. ..." stays one list.
function renderBlocks(text) {
  const blocks = [];
  let list = null;
  const flush = () => {
    if (list) blocks.push(list);
    list = null;
  };

  for (const line of text.split("\n")) {
    const ol = line.match(/^\s*(\d+)[.)]\s+(.*)$/);
    const ul = line.match(/^\s*[-*•]\s+(.*)$/);
    if (ol || ul) {
      const type = ol ? "ol" : "ul";
      if (!list || list.type !== type) {
        flush();
        list = { type, start: ol ? Number(ol[1]) : 1, items: [] };
      }
      list.items.push(ol ? ol[2] : ul[1]);
    } else if (line.trim()) {
      flush();
      blocks.push({ type: "p", text: line });
    }
  }
  flush();

  return blocks.map((block, i) => {
    if (block.type === "p") return <p key={i}>{renderInline(block.text)}</p>;
    const items = block.items.map((item, j) => <li key={j}>{renderInline(item)}</li>);
    return block.type === "ol" ? (
      <ol key={i} start={block.start}>{items}</ol>
    ) : (
      <ul key={i}>{items}</ul>
    );
  });
}

export default function Message({ message }) {
  const { role, content, sources, pending, interrupted } = message;
  return (
    <div className={`message message--${role}`}>
      <div className="bubble">
        {pending ? (
          <span className="typing" aria-label="Assistant is typing">
            <span />
            <span />
            <span />
          </span>
        ) : (
          renderBlocks(content)
        )}
        {interrupted && <p className="interrupted">(response interrupted)</p>}
      </div>
      {sources?.length > 0 && <div className="sources">Sources: {sources.join(", ")}</div>}
    </div>
  );
}
