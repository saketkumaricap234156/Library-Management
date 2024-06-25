import tornado
import json
from db import db
from datetime import datetime, timedelta
from bson import ObjectId

class MembershipHistoryhandler(tornado.web.RequestHandler):
    async def post(self):
        try:
            data=json.loads(self.request.body)
            user_id=data.get("user_id")
            membership_id = data.get("membership_id")
            
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                self.set_status(404)
                self.write({"error": "User not found"})
                return
            
            membership = await db.membership.find_one({"_id":ObjectId(membership_id)})
            if not membership:
                self.set_status(404)
                self.write({"error": "Membership not found"})
                return
            
            # await db.membershiphistory.update_many(
            #     {"user_id": ObjectId(user_id), "isactive": True},
            #     {"$set": {"isactive": False}}
            # )
            
            existing_membership = await db.membershiphistory.find_one({
            "user_id": ObjectId(user_id),
            "membership_id": ObjectId(membership_id)
            })
        
            if existing_membership:
                self.set_status(400)
                self.write({"error": "You have already added this membership"})
                return
        
            duration_in_months=membership.get('duration_in_months')
            current_date=datetime.now()
            End_Date=current_date + timedelta(duration_in_months*30)
            
            if current_date>End_Date:
                isactive=False
            else:
                isactive=True
                     
            new_membership={
            "user_id": ObjectId(user_id),
            "membership_id": ObjectId(membership_id),
            "Activation_date":current_date,
            "End_Date":End_Date,
            "isactive":isactive
        }
            await db.membershiphistory.insert_one(new_membership)            
            self.write({"status": "success", "message": "Membership added successfully"})
            
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
