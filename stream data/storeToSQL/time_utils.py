from datetime import datetime, timezone
import pytz

def enrich_with_time_info(data: dict, timestamp_field="visitStartTime") -> dict:
    ts = data.get(timestamp_field)
    if ts:
        try:
            # UTC 시간 생성
            dt_utc = datetime.utcfromtimestamp(ts).replace(tzinfo=timezone.utc)
            
            # LA 시간대로 변환
            la_tz = pytz.timezone("America/Los_Angeles")
            dt_la = dt_utc.astimezone(la_tz)
            
            data["datetime_utc"] = dt_utc.isoformat()
            data["datetime_la"] = dt_la.isoformat()
        except Exception as e:
            # 시간대 변환 실패 시 UTC만 저장
            dt_utc = datetime.utcfromtimestamp(ts)
            data["datetime_utc"] = dt_utc.isoformat()
            data["datetime_la"] = dt_utc.isoformat()  # UTC로 대체
    return data
