import React, { useEffect, useState } from "react";

export default function GPTTypingBubble({ message, time }) {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    let index = 0;

    const interval = setInterval(() => {
      if (index < message.length) {
        setDisplayedText((prev) => prev + message[index]);
        index++;
      } else {
        clearInterval(interval);
      }
    }, 30); // 타이핑 속도 조정

    return () => clearInterval(interval);
  }, [message]);

  return (
    <div className="bg-gray-100 p-3 rounded-md shadow text-left text-sm relative w-fit max-w-[80%]">
      <p className="whitespace-pre-wrap">{displayedText}</p>
      {time && (
        <span className="text-gray-400 text-xs absolute bottom-1 right-2">
          {time}
        </span>
      )}
    </div>
  );
}
