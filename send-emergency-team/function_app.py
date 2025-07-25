import azure.functions as func
import logging
import os
import requests

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="SendToTeams", methods=["POST"])
def send_to_teams(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Stream Analytics에서 요청 수신")

    try:
        # JSON 파싱 (단일 리스트)
        data = req.get_json()
        if not isinstance(data, list):
            raise ValueError("입력은 리스트 형식이어야 합니다.")
        logging.info(f"수신된 데이터: {data}")

        # StayTime 수집
        staytimes = [item.get("StayTime") for item in data if item.get("StayTime") is not None]

        # 타임스탬프 (가장 첫 WindowEnd 기준)
        window_end = data[0].get("WindowEnd", "알 수 없음")

        # 메시지 조건 처리
        if any(stay >= 17 for stay in staytimes):
            message = (
                f"[🚨 경고] {window_end}\n"
                f"병목현상으로 인한 이탈 급증이 우려됩니다. 빠른 확인 바랍니다.\n\n"
                f"🔍 분당 최대 이탈 의심 수치: {max(staytimes)}명"
            )


        logging.info(f"보낼 메시지: {message}")

        # Teams Webhook URL 설정
        webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
        if not webhook_url:
            logging.error("환경변수 TEAMS_WEBHOOK_URL이 설정되지 않았습니다.")
            return func.HttpResponse("서버 설정 오류", status_code=500)

        # Teams 메시지 전송 (MessageCard 포맷)
        teams_payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": "AI Agent Alert",
            "themeColor": "FF0000",  # 빨간색 경고
            "title": "📢 AI Agent 알림 봇",
            "text": message
        }

        response = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            json=teams_payload
        )

        if response.status_code != 200:
            logging.error(f"Teams 전송 실패: {response.status_code} {response.text}")
            return func.HttpResponse("Teams 전송 실패", status_code=500)

        logging.info("Teams 메시지 전송 성공")
        return func.HttpResponse("Function 완료", status_code=200)

    except Exception as e:
        logging.exception("처리 중 예외 발생")
        return func.HttpResponse(f"오류 발생: {str(e)}", status_code=500)
