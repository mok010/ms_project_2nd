# SendToTeamsKpi.py
import logging
import azure.functions as func
import os
import requests

SendToTeamsKpi = func.Blueprint()

TEAMS_WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_URL")

def format_teams_message(data):
    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": "📊 Daily KPI Report",
        "themeColor": "0076D7",
        "title": "📈 KPI Summary Report",
        "sections": [{
            "facts": [
                {"name": "🛒 총 상품 수량", "value": str(data.get("Total_Quantity", 0))},
                {"name": "💰 총 매출", "value": f'{data.get("Total_Revenue", 0):,.2f} ₩'},
                {"name": "🧾 거래 수", "value": str(data.get("Total_Transactions", 0))},
                {"name": "👥 세션 수", "value": str(data.get("Total_Sessions", 0))},
                {"name": "🆕 신규 방문", "value": str(data.get("New_Visit_Sessions", 0))}
            ],
            "markdown": True
        }]
    }

@SendToTeamsKpi.function_name(name="SendToTeamsKpi")
@SendToTeamsKpi.route(route="SendToTeamsKpi", methods=["POST"])
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("요청 수신됨 (SendToTeamsKpi)")

    try:
        data = req.get_json()
        if not isinstance(data, list) or not data:
            raise ValueError("입력은 최소 하나 이상의 항목을 포함한 리스트여야 합니다.")

        kpi = data[0]
        logging.info(f"KPI 데이터 수신: {kpi}")

        message = format_teams_message(kpi)
        response = requests.post(TEAMS_WEBHOOK_URL, json=message)

        if response.status_code == 200:
            return func.HttpResponse("메시지 전송 완료 ✅", status_code=200)
        else:
            logging.error(f"Teams 전송 실패: {response.text}")
            return func.HttpResponse("Teams 전송 실패", status_code=500)

    except Exception as e:
        logging.error(f"에러: {str(e)}")
        return func.HttpResponse(f"에러 발생: {str(e)}", status_code=500)
