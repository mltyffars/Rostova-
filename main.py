import datetime
from typing import Optional
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Autonomous Maintenance Factory Gateway", version="1.0.0"
)


class MaintenanceIssue(BaseModel):
    subscriber_id: str
    repository_url: str
    issue_id: str
    title: str
    description: str
    logs: Optional[str] = None


@app.get("/")
def health_check():
    return {
        "status": "online",
        "system": "Maintenance Factory Gateway",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@app.post("/webhook/maintenance")
async def receive_maintenance_issue(
    issue: MaintenanceIssue, background_tasks: BackgroundTasks
):
    if not issue.subscriber_id or not issue.repository_url:
        raise HTTPException(
            status_code=400, detail="بيانات غير مكتملة: ID والمستودع مطلوبان."
        )

    print(
        f"[{datetime.datetime.now()}] تم استقبال طلب صيانة من المشترك: {issue.subscriber_id}"
    )
    print(f"المستودع: {issue.repository_url} | المشكلة: {issue.title}")

    return {
        "status": "accepted",
        "message": "تم استقبال بلاغ الصيانة بنجاح وهو قيد المعالجة الآلية.",
        "issue_id": issue.issue_id,
        "subscriber_id": issue.subscriber_id,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
