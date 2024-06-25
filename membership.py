import tornado.web
import json
from db import create_membership, get_membership
from db import db
from bson import ObjectId

class Membershiphandler(tornado.web.RequestHandler):
    async def post(self):
        try:
            data = json.loads(self.request.body)
            admin_id=data['admin_id']
            type=data['type']
            price=data['price']
            duration_in_months=data['duration_in_months']
            benefits=data['benefits']
        except (json.JSONDecodeError, KeyError):
            self.set_status(400)
            self.write({'error': 'Invalid request format'})
            return
        
        membership_id= await create_membership(admin_id, type, price, duration_in_months, benefits)
        self.write({'status':'success', 'membership_id':membership_id})
        
    async def get(self):
        try:
        #     membership_id = self.get_argument('membership_id')
             
        #     user = await db.users.find_one(
        #          {'_id': ObjectId(membership_id)}, 
        #          {'name': 1, 'mobile': 1, 'email': 1}
        #      )
             
        #     if not user:
        #         self.set_status(404)
        #         self.write({"error": "User not found"})
        #         return
            
        #     user_details = {
        #     "name": user['name'],
        #     "mobile": user['mobile'],
        #     "email": user['email']
        # }
        #     self.write(user_details)
        
            memberships = await db.membership.find({}, {'_id': 0, 'type': 1, 'price': 1, 'duration_in_months': 1, 'benefits': 1}).to_list(length=None)
            self.write({'memberships': memberships})
         
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)}) 
            
    
    async def put(self):
        membership_id = self.get_argument('membership_id')
        try:
            data = tornado.escape.json_decode(self.request.body)
            update_result = await db.membership.update_one(
            {'_id': ObjectId(membership_id)},
            {'$set': data}
            )
            if update_result.modified_count > 0:
                self.write({'success': True})
            else:
                self.set_status(404)
                self.write({'error': 'membership not found'})
            
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)}) 
                      
    async def delete(self):  
        membership_id = self.get_argument('membership_id')
        try:
            result = await db.membership.delete_one({'_id': ObjectId(membership_id)})
            if result.deleted_count == 1:
                self.write({'status': 'success', 'message': 'membership deleted'})
            else:
                self.set_status(404)
                self.write({'status': 'error', 'message': 'membership not found'})
                
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)}) 
                
        
                   


            
             
            
            