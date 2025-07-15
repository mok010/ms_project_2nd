import React, { useState, useRef, useEffect } from "react";
import ChatBubble from "./ChatBubble";
import LoadingBubble from "./LoadingBubble";
import GPTTypingBubble from "./GPTTypingBubble";
import { formatTime } from "../utils/time";

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    const userMessage = {
      role: "user",
      text: trimmed,
      time: formatTime(),
      id: Date.now() + "-user",
    };

    const loadingMessage = {
      role: "loading",
      text: "답변 생성 중...",
      time: formatTime(),
      id: Date.now() + "-loading",
    };

    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setInput("");

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat_smart/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed }),
      });

      const data = await res.json();
      console.log("서버 응답 전체 data:", data);

      const answerRaw = data?.answer;
      console.log("answerRaw:", answerRaw);

      let answerText = "";

      if (typeof answerRaw === "string") {
        answerText = answerRaw;
      } else if (
        answerRaw &&
        typeof answerRaw === "object" &&
        "content" in answerRaw
      ) {
        answerText = String(answerRaw.content ?? "");
      } else {
        answerText = "오류가 발생했어요. 응답을 받지 못했어요.";
      }

      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          role: "assistant",
          text: answerText,
          time: formatTime(),
          id: Date.now() + "-assistant",
        },
      ]);
    } catch (err) {
      console.error("fetch 실패:", err);

      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          role: "assistant",
          text: "오류가 발생했어요. 서버 연결 실패.",
          time: formatTime(),
          id: Date.now() + "-error",
        },
      ]);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-white shadow-lg rounded-md p-4 max-w-md mx-auto mt-8">
      <div className="flex-1 overflow-auto space-y-3 mb-4">
        {messages.map((msg) => {
          if (msg.role === "loading") {
            return <LoadingBubble key={msg.id} time={msg.time} />;
          } else if (msg.role === "assistant") {
            return (
              <GPTTypingBubble
                key={msg.id}
                message={msg.text}
                time={msg.time}
              />
            );
          } else {
            return (
              <ChatBubble
                key={msg.id}
                role={msg.role}
                text={msg.text}
                time={msg.time}
              />
            );
          }
        })}
        <div ref={chatEndRef} />
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 border p-2 rounded"
          placeholder="메시지를 입력하세요"
        />
        <button
          onClick={handleSend}
          className="bg-purple-600 text-white px-4 py-2 rounded"
        >
          보내기
        </button>
      </div>
    </div>
  );
}
