import React, { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css'; // 다크 테마로 변경

const GPTMessage = ({ text, isTyping = false, onDone }) => {
  const [displayText, setDisplayText] = useState('');
  const [showMarkdown, setShowMarkdown] = useState(false);
  const indexRef = useRef(0);
  const intervalRef = useRef(null);
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    if (!isTyping) {
      // 타이핑이 아닌 경우 바로 마크다운 렌더링
      setDisplayText(text);
      setIsCompleted(true);
      setShowMarkdown(true);
      return;
    }

    if (!text) return;

    // 타이핑 시작 시 초기화
    setDisplayText('');
    setShowMarkdown(false);
    setIsCompleted(false);
    indexRef.current = 0;

    // 기존 인터벌 정리
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    intervalRef.current = setInterval(() => {
      if (indexRef.current < text.length) {
        setDisplayText(text.substring(0, indexRef.current + 1));
        indexRef.current += 1;
      } else {
        // 타이핑 완료
        clearInterval(intervalRef.current);
        setIsCompleted(true);
        setShowMarkdown(true);
        
        // 약간의 지연 후 onDone 호출 (마크다운 렌더링 완료 대기)
        setTimeout(() => {
          onDone?.();
        }, 100);
      }
    }, 30);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [text, isTyping]); // onDone을 의존성에서 제거

  const handleCopy = (code) => navigator.clipboard.writeText(code);

  const markdownContent = (
    <ReactMarkdown
      children={displayText || text} // displayText 우선 사용
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight]}
      components={{
        code({ inline, className, children, ...props }) {
          return !inline ? (
            <div className="relative group my-4">
              <pre className="overflow-x-auto p-3 bg-[#3a3a3a] text-gray-200 rounded-md text-sm border border-gray-500">
                <code className={className} {...props}>{children}</code>
              </pre>
              <button
                onClick={() => handleCopy(children)}
                className="absolute top-2 right-2 text-xs bg-gray-600 hover:bg-gray-500 text-gray-200 border border-gray-500 px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition"
              >
                복사
              </button>
            </div>
          ) : (
            <code className="bg-gray-500 text-gray-200 px-1 rounded">{children}</code>
          );
        }
      }}
    />
  );

  return (
    <div className="w-full bg-[#f7f7f8] text-black p-4 rounded-md shadow-inner text-sm leading-relaxed relative">
      {showMarkdown ? (
        <div className="markdown-content">
          {markdownContent}
        </div>
      ) : (
        <div className="whitespace-pre-wrap">{displayText || '●●●'}</div>
      )}
      
      <style jsx>{`
        .markdown-content h1 {
          font-size: 1.5em;
          font-weight: bold;
          margin: 0.5em 0;
        }
        .markdown-content h2 {
          font-size: 1.3em;
          font-weight: bold;
          margin: 0.5em 0;
        }
        .markdown-content h3 {
          font-size: 1.1em;
          font-weight: bold;
          margin: 0.5em 0;
        }
        .markdown-content ul {
          list-style-type: disc;
          margin-left: 4.5em; /* 더 많이 들여쓰기 */
          margin: 0.5em 0;
          padding-left: 0.5em; /* 추가 패딩 */
        }
        .markdown-content ol {
          list-style-type: decimal;
          margin-left: 4.5em; /* 더 많이 들여쓰기 */
          margin: 0.5em 0;
          padding-left: 1em; /* 패딩 증가 */
        }
        .markdown-content li {
          margin: 0.25em 0;
        }
        .markdown-content p {
          margin: 0.5em 0;
        }
        .markdown-content strong {
          font-weight: bold;
        }
        .markdown-content em {
          font-style: italic;
        }
        .markdown-content hr {
          border: none;
          border-top: 1px solid #ccc;
          margin: 1em 0;
        }
        
        /* 중첩된 리스트 들여쓰기 조정 */
        .markdown-content ul ul,
        .markdown-content ol ol,
        .markdown-content ul ol,
        .markdown-content ol ul {
          margin-left: 2.5em; /* 하위 리스트 들여쓰기 증가 */
          padding-left: 0.5em;
        }
      `}</style>
    </div>
  );
};

export default GPTMessage;