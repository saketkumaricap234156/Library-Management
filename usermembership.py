import tornado.ioloop
import tornado.web
import tornado.httpserver
from bson.objectid import ObjectId
import json
from db import db
import datetime 

class UserMembershipHandler(tornado.web.RequestHandler):
    async def post(self):
        try:
            data = json.loads(self.request.body)
            user_id = data.get("user_id")
            membership_id = data.get("membership_id")
            
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            membership = await db.membership.find_one({"_id":ObjectId(membership_id)})
            
            if not user:
                self.set_status(404)
                self.write({"error": "User not found"})
                return

            if not membership:
                self.set_status(404)
                self.write({"error": "Membership not found"})
                return
            
            membership_details = {
                "membership_id":membership["_id"],
                "type": membership["type"],
                "Activation_date" :datetime.datetime.now(),
                "status": "active",
               
            }
            
            update_result= await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"membership": membership_details }}
                
            )
            
            if update_result.modified_count == 1:
                self.write({"message": "Membership added successfully"})
            else:
                self.write({"message": "No changes made to the user's membership"})

        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})