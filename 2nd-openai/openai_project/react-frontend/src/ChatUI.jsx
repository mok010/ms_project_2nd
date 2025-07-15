// src/ChatUI.jsx
import React, { useState } from "react";
import axios from "axios";

const ChatUI = () => {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
        const res = await axios.post("http://127.0.0.1:8000/api/chat_smart/", {
        question: input
        });
        console.log("서버 응답:", res.data);
        setResponse(res.data.answer);
    } catch (err) {
        console.error("오류 발생:", err);
        setResponse("에러 발생. 서버 확인해봐.");
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="질문을 입력하세요"
          style={{ padding: "0.5rem", width: "300px" }}
        />
        <button type="submit" style={{ marginLeft: "1rem" }}>
          전송
        </button>
      </form>
      <div style={{ marginTop: "2rem" }}>
        <strong>답변:</strong>
        <p>{response}</p>
      </div>
    </div>
  );
};

export default ChatUI;
