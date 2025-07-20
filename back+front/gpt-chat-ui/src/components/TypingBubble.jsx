import React, { useState, useEffect } from 'react';

const TypingBubble = ({ text, onDone }) => {
  const [displayText, setDisplayText] = useState('');
  const [dotCount, setDotCount] = useState(1);

  // ●●● 깜빡이는 점 (계속 돌아감)
  useEffect(() => {
    const dotInterval = setInterval(() => {
      setDotCount((prev) => (prev % 3) + 1); // 1 -> 2 -> 3 -> 1...
    }, 500);
    return () => clearInterval(dotInterval);
  }, []);

  // GPT 텍스트가 오면 타이핑 시작
  useEffect(() => {
    if (!text) return;

    let i = 0;
    const typeInterval = setInterval(() => {
      setDisplayText((prev) => prev + text[i]);
      i++;
      if (i >= text.length) {
        clearInterval(typeInterval);
        if (onDone) onDone();
      }
    }, 30);

    return () => clearInterval(typeInterval);
  }, [text, onDone]);

  return (
    <div className="bg-gray-100 px-4 py-2 rounded-lg rounded-bl-none max-w-[75%] text-sm font-[450] whitespace-pre-wrap">
      {text ? displayText : '●'.repeat(dotCount)}
    </div>
  );
};

export default TypingBubble;
