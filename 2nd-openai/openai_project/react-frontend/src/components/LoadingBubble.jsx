export default function LoadingBubble({ time }) {
  return (
    <div className="flex justify-start">
      <div className="bg-gray-200 p-3 rounded-xl text-black max-w-xs">
        <div className="animate-pulse text-gray-500">답변 생성 중...</div>
        <div className="text-xs text-gray-400 mt-1 text-right">{time}</div>
      </div>
    </div>
  );
}