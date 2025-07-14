import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./ChatBox.css";

function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const chatRef = useRef(null);

  const sendMessage = async () => {
    if (!question.trim()) return;

    const newMessages = [...messages, { type: "user", text: question }];
    setMessages(newMessages);
    setQuestion("");
    setLoading(true);

    try {
      const response = await axios.post("http://localhost:8000/chatbot/", {
        question,
      });
      const botMessage = { type: "bot", text: response.data.answer };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          type: "error",
          text: "서버 응답에 실패했어요. Django가 켜져 있는지 확인해주세요.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  useEffect(() => {
    chatRef.current?.scrollTo(0, chatRef.current.scrollHeight);
  }, [messages, loading]);

  const quickReplies = ["전체 사용자 수", "새 방문자 수", "총 주문 수"];

  return (
    <div className="layout-wrapper">
      <nav className="nav-bar">
        <h2>데이터 챗봇</h2>
      </nav>

      <div className="main-container">
        <div className="chat-section">
          <div className="quick-replies">
            {quickReplies.map((qr, idx) => (
              <button key={idx} onClick={() => setQuestion(qr)}>
                {qr}
              </button>
            ))}
          </div>

          <div className="chat-box" ref={chatRef}>
            {messages.map((msg, i) => (
              <div key={i} className={`message-row ${msg.type}`}>
                {msg.type === "bot" && <img src="/bot.png" className="avatar" />}
                <div className={`message-bubble ${msg.type}`}>{msg.text}</div>
                {msg.type === "user" && <img src="/user.png" className="avatar user-right" />}
              </div>
            ))}
            {loading && (
              <div className="message-row bot">
                <img src="/bot.png" className="avatar" />
                <div className="message-bubble">입력 중...</div>
              </div>
            )}
          </div>

          <div className="input-area">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="질문을 입력하세요..."
            />
            <button onClick={sendMessage}>보내기</button>
          </div>
        </div>

        <div className="history-section">
          <h4>채팅 기록</h4>
          <ul className="history-list">
            <li>전체 사용자 수</li>
            <li>새 방문자 수</li>
            <li>총 주문 수</li>
            <li>...</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ChatBox;
