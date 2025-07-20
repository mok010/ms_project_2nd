import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import GPTMessage from './GPTMessage';
import ChatInput from './ChatInput';
import LoadingDots from './LoadingDots';

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [currentTypingText, setCurrentTypingText] = useState('');
  const [typingId, setTypingId] = useState(null);
  const [atBottom, setAtBottom] = useState(true);
  const [abortController, setAbortController] = useState(null);
  const containerRef = useRef(null);
  const typingRef = useRef(null);

  const handleSend = async () => {
    if (!input.trim() || isWaitingForResponse || isTyping) return;

    const userMessage = { role: 'user', text: input, id: Date.now() };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsWaitingForResponse(true);

    // AbortController 생성
    const controller = new AbortController();
    setAbortController(controller);

    try {
      const gptReply = await GptResponse(input, controller.signal);
      const id = Date.now();
      setTypingId(id);
      setCurrentTypingText(gptReply);
      setIsWaitingForResponse(false);
      setIsTyping(true);
      setAbortController(null);
    } catch (error) {
      setIsWaitingForResponse(false);
      setIsTyping(false);
      setAbortController(null);
      
      if (error.name === 'AbortError') {
        console.log('요청이 중단되었습니다.');
        return;
      }
      
      console.error('응답 받기 실패:', error);
      // 에러 메시지도 messages에 추가
      const errorMessage = { 
        role: 'gpt', 
        text: '서버와 연결할 수 없습니다. 나중에 다시 시도해주세요.', 
        id: Date.now() 
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const handleStop = () => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
    }
    
    // 중단 메시지만 표시
    setMessages((prev) => [...prev, { 
      role: 'gpt', 
      text: '생성이 중단됨', 
      id: Date.now(),
      isStopped: true  // 중단된 메시지임을 표시
    }]);
    
    setIsWaitingForResponse(false);
    setIsTyping(false);
    setCurrentTypingText('');
    setTypingId(null);
  };

  const handleTypingDone = () => {
    console.log('타이핑 완료됨:', currentTypingText); // 디버깅용
    setMessages((prev) => [...prev, { role: 'gpt', text: currentTypingText, id: typingId }]);
    setIsTyping(false);
    setCurrentTypingText('');
    setTypingId(null);
  };

  useEffect(() => {
    if ((isWaitingForResponse || isTyping) && typingRef.current) {
      typingRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [currentTypingText, isWaitingForResponse, isTyping]);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const onScroll = () => {
      const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 100;
      setAtBottom(nearBottom);
    };
    el.addEventListener('scroll', onScroll);
    return () => el.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    if (atBottom) {
      containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [messages, isWaitingForResponse, isTyping, atBottom]);

  // 타이핑 상태 변화 감지 (디버깅용)
  useEffect(() => {
    console.log('타이핑 상태:', { isTyping, currentTypingText: currentTypingText.length });
  }, [isTyping, currentTypingText]);

  return (
    <div className="w-full h-screen bg-[#F5F1FA] flex justify-center relative">
      <div className="w-full max-w-screen-lg h-full flex flex-col"
        style={{
          background: 'linear-gradient(180deg, #764ba2 0%, #F5F1FA 15%)'
        }}
      >
        {/* ChatBot 헤더 바 */}
        <div className="bg-gradient-to-r from-[#667eea] to-[#764ba2] text-white px-6 py-4 shadow-lg">
          <div className="flex items-center justify-center space-x-3">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <h1 className="text-xl font-bold tracking-wide">ChatBot</h1>
            <div className="w-2 h-2 bg-blue-300 rounded-full animate-bounce"></div>
          </div>
          <div className="text-center text-sm text-blue-100 mt-1 opacity-90">
            AI Assistant
          </div>
        </div>
        <div 
          ref={containerRef} 
          className="flex-1 overflow-y-auto px-4 py-6 space-y-6 scroll-smooth bg-[#F5F1FA]"
          style={{
            scrollbarWidth: 'thin',
            scrollbarColor: '#9CA3AF transparent'
          }}
        >
          {messages.map((msg) => (
            <div key={msg.id} className={msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
              {msg.role === 'user' ? (
                <div className="bg-[#AE57FF] text-white px-4 py-2 rounded-lg rounded-br-none max-w-[75%] text-sm whitespace-pre-wrap shadow-sm">
                  {msg.text}
                </div>
              ) : (
                <div className="w-full">
                  {msg.isStopped ? (
                    <div className="bg-[#f7f7f8] text-gray-500 p-4 rounded-md shadow-inner text-sm text-center">
                      {msg.text}
                    </div>
                  ) : (
                    <GPTMessage text={msg.text} />
                  )}
                </div>
              )}
            </div>
          ))}

          {isWaitingForResponse && (
            <div className="flex justify-start" ref={typingRef}>
              <div className="w-full">
                <LoadingDots />
              </div>
            </div>
          )}

          {isTyping && (
            <div className="flex justify-start" ref={typingRef}>
              <div className="w-full">
                <GPTMessage 
                  text={currentTypingText} 
                  isTyping={true} 
                  onDone={handleTypingDone}
                  key={typingId} // 키를 추가해서 새로운 메시지마다 새로 렌더링
                />
              </div>
            </div>
          )}
        </div>

        {!atBottom && (
          <div className="absolute bottom-32 left-1/2 transform -translate-x-1/2 z-10">
            <button
              className="bg-white border shadow px-4 py-2 rounded-full text-sm hover:bg-gray-50 transition border-gray-200"
              onClick={() =>
                containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight, behavior: 'smooth' })
              }
            >
              ↓ 아래로 이동
            </button>
          </div>
        )}

        <ChatInput
          input={input}
          setInput={setInput}
          onSubmit={handleSend}
          isDisabled={isWaitingForResponse || isTyping}
          isGenerating={isWaitingForResponse || isTyping}
          onStop={handleStop}
        />
      </div>
      
      <style jsx>{`
        .w-full::-webkit-scrollbar {
          width: 8px;
        }
        .w-full::-webkit-scrollbar-track {
          background: transparent;
        }
        .w-full::-webkit-scrollbar-thumb {
          background: #9CA3AF;
          border-radius: 4px;
          opacity: 0.6;
        }
        .w-full::-webkit-scrollbar-thumb:hover {
          background: #6B7280;
          opacity: 0.8;
        }
      `}</style>
    </div>
  );
};

export const GptResponse = async (prompt, signal) => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/chat_smart/', {
      question: prompt
    }, {
      signal // AbortController signal 전달
    });
    return response.data.answer;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw error; // abort 에러는 그대로 throw
    }
    console.error('백엔드 API 호출 실패:', error);
    return '서버와 연결할 수 없습니다. 나중에 다시 시도해주세요.';
  }
};

export default ChatWindow;