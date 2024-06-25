import tornado.ioloop
import tornado.web
import bcrypt
import json
import motor.motor_tornado

from RegisterHandler import BaseHandler
from db import db

class LoginHandler(BaseHandler):
    async def post(self):
        data=json.loads(self.request.body)
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        if not email or not password or not role:
            self.set_status(400)
            self.write({"error": "email, password, and role are required"})
            return
        
        if role=='admin':
            collection=db.admin
        elif role=='manager':
            collection=db.managers
        else:
            collection=db.users

        user = await collection.find_one({'email': email})
        if not user:
            self.set_status(400)
            self.write({"error": "Invalid email or password"})
            return

        if role=="admin":
            if await db.admin.find_one({'password':password}):
                self.write({"message": "Admin login successful"})
            else:
                self.set_status(400)
                self.write({"message":"Invalid Email or Password"})
        elif role=='manager':
            if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                self.write({"message": "Manager login successful"})
            else:
                self.set_status(400)
                self.write({"message":"Invalid Email or Password"})
        else:
            if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                self.write({"user_id": str(user['_id'])})
            else:
                self.set_status(400)
                self.write({"message":"Invalid Email or Password"})
 
        