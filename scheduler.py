import tornado.ioloop
import tornado.web
import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from datetime import datetime, timedelta
from db import db
collection = db.scheduler

def send_email(to_address, subject, body):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'aryanasa893@gmail.com'
    smtp_password = 'pvtd iucf cbev wite'

    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_address
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))

    try:
        smtp = smtplib.SMTP(smtp_server, smtp_port)
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(smtp_username, to_address, msg.as_string())
        smtp.quit()
        print(f"Email sent successfully to {to_address}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

async def scheduler_task():
    while True:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tasks = collection.find({"start_time": {"$lte": current_time}})
        async for task in tasks:
            print(f"Scheduler started at {current_time} for task {task['_id']}")
            task_data = task.get('data', {})
            if 'email' in task_data and 'to' in task_data['email'] and 'subject' in task_data['email'] and 'body' in task_data['email']:
                email_data = task_data['email']
                to_address = email_data['to']
                subject = email_data['subject']
                body = email_data['body']
                success = send_email(to_address, subject, body)
                if success:
                    print("Email sent successfully.")
                    await collection.delete_one({"_id": task['_id']})
                else:
                    print("Failed to send email.")
        await asyncio.sleep(60)

class ScheduleHandler(tornado.web.RequestHandler):
    async def post(self):
        try:
            data = json.loads(self.request.body)
            start_time = data.get('start_time')
            task_data = data.get('data')
            if not start_time or not task_data:
                raise ValueError("Missing 'start_time' or 'data' fields")
        except json.JSONDecodeError as e:
            self.set_status(400)
            self.write({"status": "error", "message": "Invalid JSON data"})
            return
        except ValueError as e:
            self.set_status(400)
            self.write({"status": "error", "message": str(e)})
            return

        task = {"start_time": start_time, "data": task_data}
        result = await collection.insert_one(task)
        task_id = str(result.inserted_id)

        self.write({"status": "success", "task_id": task_id})

def make_app():
    return tornado.web.Application([
        (r"/schedule", ScheduleHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)

    loop = tornado.ioloop.IOLoop.current()
    loop.add_callback(scheduler_task)

    loop.start()
