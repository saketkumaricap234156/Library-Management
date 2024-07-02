import tornado.ioloop
import tornado.web
import bcrypt
import json
import motor.motor_tornado
from bson import ObjectId
from datetime import date
import datetime
from db import db
class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

class RegisterHandler(BaseHandler):
    async def post(self):
        try:
            data=json.loads(self.request.body)
            name = data.get('name')
            email=data.get('email')
            mobile=int(data.get('mobile'))
            password = data.get('password')
            
            if not email or not password or not name or not mobile:
                self.set_status(400)
                self.write({"error": "email, password, name or mobile are required"})
                return

            collection = db.users

            existing_email = await collection.find_one({'email': email})
            existing_mobile = await collection.find_one({'mobile': mobile})
            
            if existing_email or existing_mobile:
                self.set_status(400)
                self.write({"error": "User already exists"})
                return

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            register_date =datetime.datetime.now()
            await collection.insert_one({'name': name, 'email':email, 'password': hashed_password, 'mobile':mobile, 'register_date':register_date})
            self.write({"message": "User registered successfully"})
            
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
        
    async def get(self):
        try:
            user_id = self.get_argument('user_id')

            user = await db.users.find_one(
                {'_id': ObjectId(user_id)},
                {'name': 1, 'mobile': 1, 'email': 1}
            )

            if not user:
                self.set_status(404)
                self.write({"error": "User not found"})
                return

            membership_history = await db.membershiphistory.find_one(
                {'user_id': ObjectId(user_id)},
                {'membership_id': 1, 'Activation_date': 1, 'End_Date': 1, 'isactive': 1}
            )
            
            if membership_history:
                if membership_history['isactive']:
                    membership = await db.membership.find_one(
                        {'_id': membership_history['membership_id']},
                        {'type': 1, 'duration_in_months': 1, 'price': 1}
                    )

                    if membership:
                        membership_details = {
                            "type": membership['type'],
                            "duration_in_months": membership['duration_in_months'],
                            "price": membership['price'],
                            "Activation_date": membership_history['Activation_date'].strftime('%Y-%m-%d') if membership_history['Activation_date'] else None,
                            "End_Date": membership_history['End_Date'].strftime('%Y-%m-%d') if membership_history['End_Date'] else None,
                            "isactive": membership_history['isactive']
                        }
                    else:
                        membership_details = {"error": "Membership type not found"}
                else:
                    membership_details = {}
            else:
                membership_details = {}

            
            user_details = {
                "name": user['name'],
                "mobile": user['mobile'],
                "email": user['email'],
                "membership": membership_details
            }

            self.write(user_details)

        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
        
    async def put(self):
        user_id=self.get_argument('user_id')
        data = tornado.escape.json_decode(self.request.body)
        if 'old_password' in data and 'new_password' in data:
            user = await db.users.find_one({'_id': ObjectId(user_id)})
            if user:
                     old_password = data['old_password']
                     user_password = user.get('password')
                     if bcrypt.checkpw(old_password.encode('utf-8'),user_password):
                        new_password = data['new_password']
                        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                        
                        update_result = await db.users.update_one(
                            {'_id': ObjectId(user_id)},
                            {'$set': {'password': hashed_password}}
                        )
                        
                        if update_result.modified_count:
                            self.write({'success': True})
                        else:
                            self.set_status(500)
                            self.write({'error': 'Password update failed'})
                     else:
                        self.set_status(401)
                        self.write({'error': 'Old password incorrect'})
            else:
                self.set_status(404)
                self.write({'error': 'User not found'})
        else:
            update_result = await db.users.update_one(
                {'_id': user_id},
                {'$set': data}
            )
            
            if update_result.modified_count:
                self.write({'success': True})
            else:
                self.set_status(404)
                self.write({'error': 'User not found'})
                
class Updateuserhandler(BaseHandler):
    async def put(self):
        try:
            user_id = self.get_argument('user_id')
            data = tornado.escape.json_decode(self.request.body)
    
            if 'old_password' in data:
                user = await db.users.find_one({'_id': ObjectId(user_id)})
                if user:
                    old_password = data['old_password']
                    user_password = user.get('password')
            
                    if bcrypt.checkpw(old_password.encode('utf-8'), user_password):
                        update_data = {}
                        if 'name' in data:
                            update_data['name'] = data['name']
                        if 'mobile' in data:
                            update_data['mobile'] = data['mobile']
                        if 'email' in data:
                            update_data['email'] = data['email']
                
                        update_result = await db.users.update_one(
                            {'_id': ObjectId(user_id)},
                            {'$set': update_data}
                            )
                
                        if update_result.modified_count:
                            self.write({'success': True})
                        else:
                            self.set_status(500)
                            self.write({'error': 'User details update failed'})
                    else:
                        self.set_status(401)
                        self.write({'error': 'Password incorrect'})
                else:
                    self.set_status(404)
                    self.write({'error': 'User not found'})
            else:
                self.set_status(400)
                self.write({'error': 'Old password required for updates'})
                
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
                    
                
                