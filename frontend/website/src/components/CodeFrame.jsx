/** Visual "screenshot" of vulnerable source code with highlighted bad lines. */
export default function CodeFrame({ frame }) {
  if (!frame) return null;
  const start = frame.start_line || 1;
  const highlights = new Set(frame.highlight_lines || []);

  return (
    <figure className="ng-code-shot">
      <figcaption>
        <span className="ng-code-dots" aria-hidden>
          <i /><i /><i />
        </span>
        <span className="ng-code-path">{frame.filename}</span>
        {frame.title && <span className="ng-code-tag">{frame.title}</span>}
      </figcaption>
      <pre className="ng-code-body">
        {(frame.lines || []).map((line, idx) => {
          const ln = start + idx;
          const bad = highlights.has(ln);
          return (
            <div key={ln} className={bad ? "ng-code-line bad" : "ng-code-line"}>
              <span className="ng-code-ln">{ln}</span>
              <code>{line || " "}</code>
            </div>
          );
        })}
      </pre>
    </figure>
  );
}
