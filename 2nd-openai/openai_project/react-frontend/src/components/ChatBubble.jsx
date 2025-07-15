export default function ChatBubble({ role, text, time }) {
  const isUser = role === "user";
  const bubbleStyle = isUser
    ? "bg-purple-600 text-white ml-auto"
    : "bg-gray-200 text-black";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`p-3 rounded-xl max-w-xs whitespace-pre-line ${bubbleStyle}`}>
        <div>{text}</div>
        <div className="text-xs text-gray-400 mt-1 text-right">{time}</div>
      </div>
    </div>
  );
}