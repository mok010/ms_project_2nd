export function formatTime() {
  const now = new Date();
  return now.toLocaleTimeString("ko-KR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}
