import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import type { Components } from 'react-markdown'

interface MarkdownPreviewProps {
  content: string
}

export function MarkdownPreview({ content }: MarkdownPreviewProps) {
  const components: Components = {
    code({ className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '')
      const language = match ? match[1] : ''
      const code = String(children).replace(/\n$/, '')

      if (language) {
        return (
          <SyntaxHighlighter
            language={language}
            style={oneLight}
            PreTag="div"
            customStyle={{
              margin: 0,
              borderRadius: '8px',
              fontSize: '0.9rem',
            }}
          >
            {code}
          </SyntaxHighlighter>
        )
      }

      return (
        <code className={className} {...props}>
          {children}
        </code>
      )
    },
  }

  return (
    <div className="markdown-preview h-full overflow-auto p-6">
      {content ? (
        <ReactMarkdown components={components}>{content}</ReactMarkdown>
      ) : (
        <div className="text-gray-400 italic">预览区域为空，开始在左侧输入 Markdown 吧...</div>
      )}
    </div>
  )
}
