import structlog
from app.core.config import get_settings
from app.models.meeting import Meeting

logger = structlog.get_logger()


import zoneinfo

def _build_reminder_email(meeting: Meeting) -> str:
    start = ""
    if meeting.start_time:
        ist_time = meeting.start_time.astimezone(zoneinfo.ZoneInfo("Asia/Kolkata"))
        start = ist_time.strftime("%A, %B %d at %I:%M %p IST")
    join = f'<a href="{meeting.meet_url}" style="display:inline-block;padding:12px 24px;background:#0066CC;color:#fff;text-decoration:none;border-radius:6px;">Join Meeting</a>' if meeting.meet_url else ""
    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>MeetEdge Reminder</title></head>
<body style="font-family:system-ui,sans-serif;background:#0F172A;color:#f4f4f5;padding:24px;">
<div style="max-width:560px;margin:0 auto;">
  <h1 style="color:#0066CC;">MeetEdge</h1>
  <p>Your meeting is coming up:</p>
  <h2>{meeting.title}</h2>
  <p><strong>{start}</strong></p>
  <p>{join}</p>
  <p style="color:#64748B;font-size:12px;">— MeetEdge by Secure Edge Pvt Ltd</p>
</div>
</body>
</html>
"""


def _build_bot_joining_email(meeting: Meeting) -> str:
    start = ""
    if meeting.start_time:
        ist_time = meeting.start_time.astimezone(zoneinfo.ZoneInfo("Asia/Kolkata"))
        start = ist_time.strftime("%A, %B %d at %I:%M %p IST")
    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>MeetEdge Bot Joining</title></head>
<body style="font-family:system-ui,sans-serif;background:#0F172A;color:#f4f4f5;padding:24px;">
<div style="max-width:560px;margin:0 auto;">
  <h1 style="color:#0066CC;">MeetEdge</h1>
  <p>The MeetEdge bot will join your upcoming meeting to take notes and capture action items:</p>
  <h2>{meeting.title}</h2>
  <p><strong>{start}</strong></p>
  <p style="color:#64748B;font-size:12px;">— MeetEdge by Secure Edge Pvt Ltd</p>
</div>
</body>
</html>
"""


def _build_summary_email(meeting: Meeting) -> str:
    summary = meeting.summary or "No summary available."
    items = ""
    if meeting.action_items:
        items = "<ul>" + "".join(f"<li>{ai.text}" + (f" (assignee: {ai.assignee_email})" if ai.assignee_email else "") + "</li>" for ai in meeting.action_items) + "</ul>"
    join = f'<a href="{meeting.meet_url}">Meeting link</a>' if meeting.meet_url else ""
    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>MeetEdge Summary</title></head>
<body style="font-family:system-ui,sans-serif;background:#0F172A;color:#f4f4f5;padding:24px;">
<div style="max-width:560px;margin:0 auto;">
  <h1 style="color:#0066CC;">MeetEdge</h1>
  <h2>Meeting summary: {meeting.title}</h2>
  <h3>Executive summary</h3>
  <p>{summary}</p>
  <h3>Action items</h3>
  {items}
  <p>{join}</p>
  <p style="color:#64748B;font-size:12px;">— MeetEdge by Secure Edge Pvt Ltd</p>
</div>
</body>
</html>
"""


class NotificationService:
    def __init__(self):
        self.settings = get_settings()

    async def send_email(self, to_emails: list[str], subject: str, body_html: str) -> None:
        if not self.settings.smtp_username or not self.settings.smtp_password:
            logger.warning("smtp_not_configured", message="SMTP_USERNAME/SMTP_PASSWORD not set, skipping email")
            return
        try:
            import aiosmtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.settings.smtp_from_email
            msg["To"] = ", ".join(to_emails)
            msg.attach(MIMEText(body_html, "html"))
            await aiosmtplib.send(
                msg,
                hostname=self.settings.smtp_host,
                port=self.settings.smtp_port,
                username=self.settings.smtp_username,
                password=self.settings.smtp_password,
                start_tls=True,
            )
        except Exception as e:
            logger.error("send_email_failed", to=to_emails, error=str(e), exc_info=True)

    async def send_meeting_reminder(self, meeting: Meeting, attendee_emails: list[str]) -> None:
        if not attendee_emails:
            return
        try:
            body = _build_reminder_email(meeting)
            await self.send_email(
                attendee_emails,
                f"Reminder: {meeting.title}",
                body,
            )
        except Exception as e:
            logger.error("send_meeting_reminder_failed", meeting_id=meeting.id, error=str(e), exc_info=True)

    async def send_summary_ready(self, meeting: Meeting, attendee_emails: list[str]) -> None:
        if not attendee_emails:
            return
        try:
            body = _build_summary_email(meeting)
            await self.send_email(
                attendee_emails,
                f"Summary ready: {meeting.title}",
                body,
            )
        except Exception as e:
            logger.error("send_summary_ready_failed", meeting_id=meeting.id, error=str(e), exc_info=True)

    async def send_bot_joining_email(self, meeting: Meeting, attendee_emails: list[str]) -> None:
        if not attendee_emails:
            return
        try:
            body = _build_bot_joining_email(meeting)
            await self.send_email(
                attendee_emails,
                f"MeetEdge Bot will join: {meeting.title}",
                body,
            )
        except Exception as e:
            logger.error("send_bot_joining_email_failed", meeting_id=meeting.id, error=str(e), exc_info=True)

    async def send_slack_message(self, channel: str, text: str, blocks: list | None = None) -> None:
        if not self.settings.slack_bot_token:
            logger.warning("slack_not_configured", message="SLACK_BOT_TOKEN not set, skipping Slack message")
            return
        try:
            from slack_sdk.web.async_client import AsyncWebClient
            client = AsyncWebClient(token=self.settings.slack_bot_token)
            await client.chat_postMessage(channel=channel, text=text, blocks=blocks)
        except Exception as e:
            logger.error("send_slack_message_failed", channel=channel, error=str(e), exc_info=True)

    async def send_slack_reminder(self, meeting: Meeting) -> None:
        try:
            text = f"Reminder: {meeting.title} starting soon. Join: {meeting.meet_url or 'N/A'}"
            await self.send_slack_message(channel="#meetings", text=text)
        except Exception as e:
            logger.error("send_slack_reminder_failed", meeting_id=meeting.id, error=str(e), exc_info=True)
