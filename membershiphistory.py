import tornado
import json
from db import db
from datetime import datetime, timedelta
from bson import ObjectId
from RegisterHandler import BaseHandler
import tornado.gen

class MembershipHistoryhandler(tornado.web.RequestHandler):
    async def post(self):
        try:
            data = json.loads(self.request.body)
            user_id = data.get("user_id")
            membership_id = data.get("membership_id")
            
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                self.set_status(404)
                self.write({"error": "User not found"})
                return
            
            membership = await db.membership.find_one({"_id": ObjectId(membership_id)})
            if not membership:
                self.set_status(404)
                self.write({"error": "Membership not found"})
                return
            
            active_membership = await db.membershiphistory.find_one({
                "user_id": ObjectId(user_id),
                "isactive": True
            })
            
            if active_membership:
                self.set_status(400)
                self.write({"error": "You already have an active membership"})
                return
            
            duration_in_months = membership.get('duration_in_months')
            current_date = datetime.now()
            end_date = current_date + timedelta(days=duration_in_months * 30)
            
            isactive = current_date <= end_date
            
            new_membership = {
                "user_id": ObjectId(user_id),
                "membership_id": ObjectId(membership_id),
                "Activation_date": current_date,
                "End_Date": end_date,
                "isactive": isactive
            }
            
            await db.membershiphistory.insert_one(new_membership)
            self.write({"status": "success", "message": "Membership added successfully"})
        
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})

async def update_membership_status():
    try:
        current_date = datetime.now()
        result = await db.membershiphistory.update_many(
            {"End_Date": {"$lt": current_date}, "isactive": True},
            {"$set": {"isactive": False}}
        )
        # print(f"Updated {result.modified_count} memberships to inactive status.")
    except Exception as e:
        print(f"Error updating membership status: {str(e)}")

def schedule_membership_updates():
    tornado.ioloop.PeriodicCallback(update_membership_status, 1000).start()
    