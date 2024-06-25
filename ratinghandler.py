import tornado.web
import json
from bson import ObjectId
from db import db
from datetime import datetime

class RatingHandler(tornado.web.RequestHandler):
    async def post(self):
        try:
            data = json.loads(self.request.body)
            user_id = data.get('user_id')
            book_id = data.get('book_id')
            rating = data.get('rating')
            comment = data.get('comment')

            if not user_id or not book_id or not rating or comment is None:
                self.set_status(400)
                self.write({"status": "error", "message": "Missing required fields"})
                return

            comment_date = datetime.now()

            existing_feedback = await db.feedbacks.find_one({"user_id": ObjectId(user_id), "book_id": ObjectId(book_id)})

            if existing_feedback:
                await db.feedbacks.update_one(
                    {"_id": existing_feedback["_id"]},
                    {
                        "$set": {"rating": rating},
                        "$push": {"comments": {"comment": comment, "comment_date": comment_date}}
                    }
                )
                self.write({"status": "updated", "feedback_id": str(existing_feedback["_id"])})
            else:
                result = await db.feedbacks.insert_one({
                    "user_id": ObjectId(user_id),
                    "book_id": ObjectId(book_id),
                    "rating": rating,
                    "comments": [{"comment": comment, "comment_date": comment_date}]
                })
                self.write({"status": "created", "feedback_id": str(result.inserted_id)})

        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
            
    async def get(self):
        try:
            feedback_id=self.get_argument('feedback_id')
            feedback = await db.feedbacks.find_one({"_id": ObjectId(feedback_id)})
            if feedback:
                feedback["_id"] = str(feedback["_id"])
                self.write(feedback)
            else:
                self.set_status(404)
                self.write({"error": "Feedback not found"})
        except Exception as e:
            self.set_status(400)
            self.write({"error": str(e)})
            
    async def delete(self):
        try:
            feedback_id=self.get_argument('feedback_id')
            feedback = await db.feedbacks.find_one({"_id": ObjectId(feedback_id)})
            if feedback:
                await db.feedbacks.delete_one({"_id": ObjectId(feedback_id)})
                self.write({"status": "deleted", "feedback_id": feedback_id})
            else:
                self.set_status(404)
                self.write({"status": "error", "message": "Feedback not found"})
        except Exception as e:
            self.set_status(400)
            self.write({"status": "error", "message": str(e)})
            
                            
                
        
        