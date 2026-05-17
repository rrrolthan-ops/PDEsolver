import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

interface Props {
  source: string;
}

/**
 * Render Markdown with inline / display math.
 *
 * The pedagogical templates write inline math as `$…$`, which
 * `remark-math` + `rehype-katex` interpret transparently. This keeps
 * the templates readable in plain text.
 */
export function Markdown({ source }: Props) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeKatex]}
    >
      {source}
    </ReactMarkdown>
  );
}
