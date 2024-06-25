import tornado.web
import json
import smtplib
from email.message import EmailMessage
from itsdangerous import URLSafeTimedSerializer
from tornado.ioloop import IOLoop
from random import randint
from settings import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, SECRET_KEY
from db import db

# Initialize the URL serializer
serializer = URLSafeTimedSerializer(SECRET_KEY)

def send_otp_email(email, otp):
    msg = EmailMessage()
    msg.set_content(f"Your OTP code is: {otp}")
    msg['Subject'] = 'OTP Verification'
    msg['From'] = EMAIL_USER
    msg['To'] = email

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)

class AdminGenerateOtpHandler(tornado.web.RequestHandler):
    async def post(self):
        try:
            data = json.loads(self.request.body)
            email = data['email']
        except (json.JSONDecodeError, KeyError):
            self.set_status(400)
            self.write({'error': 'Invalid request format'})
            return

        user = await db.admin.find_one({'email': email}) or await db.users.find_one({'email': email}) or await db.manager.find_one({'email': email}) 
        if not user:
            self.set_status(404)
            self.write({'error': 'User not found'})
            return
        
        otp = randint(100000, 999999)
        await db.otp.insert_one({
            'email': email,
            'otp': str(otp)
        })

        send_otp_email(email, otp)
        self.write({'status': 'success', 'message': 'OTP sent to email'})

class AdminLoginHandler(tornado.web.RequestHandler):
    async def post(self):
        try:
            data = json.loads(self.request.body)
            email = data['email']
            otp = data['otp']
        except (json.JSONDecodeError, KeyError):
            self.set_status(400)
            self.write({'error': 'Invalid request format'})
            return

        otp_record = await db.otp.find_one({'email': email, 'otp': otp})
        if not otp_record:
            self.set_status(401)
            self.write({'error': 'Invalid OTP'})
            return

        await db.otp.delete_many({'email': email,'otp':otp})
        self.write({'status': 'success', 'message': 'Login successful'})
