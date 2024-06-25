import tornado.ioloop
import tornado.web
from db import db
from bson import ObjectId
from datetime import datetime

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()
    
class UserHandler(BaseHandler):
    async def get(self):
        try:
            user_id = self.get_argument('user_id')
            fetch_type = self.get_argument('fetch', 'all')

            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                self.set_status(404)
                self.write({"error": "User not found"})
                return
            
            def format_date(obj):
                if isinstance(obj, dict):
                    return {k: format_date(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [format_date(i) for i in obj]
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                else:
                    return obj

            if fetch_type == 'membership':
                membership_history = await db.membershiphistory.find({"user_id": ObjectId(user_id)}).to_list(length=None)
                response = {
                    "status": "success",
                    "memberships": []
                }
                for membership in membership_history:
                    membership_id = str(membership["membership_id"])
                    member_info = await db.membership.find_one({"_id": ObjectId(membership_id)}, {"_id": 0, "type": 1})
                    if not member_info:
                        continue
                    membership_data = {
                        "membership_type": member_info['type'],
                        "Activation_date": format_date(membership.get("Activation_date")),
                        "End_Date": format_date(membership.get("End_Date")),
                        "isactive": membership.get("isactive")
                    }
                    response["memberships"].append(membership_data)

                self.write(response)
                return
            
            if fetch_type == 'reading_history':
                userlibrary = await db.userlibrary.find({"user_id": ObjectId(user_id), "isactive": False}).to_list(length=None)
                comments = await db.feedbacks.find({"user_id": ObjectId(user_id)}).to_list(length=None)

                book_comments = {}
                for comment in comments:
                    book_id = str(comment["book_id"])
                    if book_id not in book_comments:
                        book_comments[book_id] = []
                    book_comments[book_id].append({
                        "comment": comment["comments"]
                    })

                response = {
                    "status": "success",
                    "reading_book_history": []
                }
                
                for book in userlibrary:
                    book_id = str(book["book_id"])
                    book_info = await db.ebooks.find_one({"_id": ObjectId(book_id)}, {"_id": 0, "title": 1})
                    if not book_info:
                        continue
                    
                    book_data = {
                        "book_name": book_info["title"],
                        "details": {
                            "collection_date": format_date(book.get("collection_date")),
                            "comments": format_date(book_comments.get(book_id, []))
                        }
                    }

                    response["reading_book_history"].append(book_data)

                self.write(response)
                return

            if fetch_type == 'active_books':
                userlibrary = await db.userlibrary.find({"user_id": ObjectId(user_id), "isactive": True}).to_list(length=None)
                comments = await db.feedbacks.find({"user_id": ObjectId(user_id)}).to_list(length=None)
                
                book_comments = {}
                for comment in comments:
                    book_id = str(comment["book_id"])
                    if book_id not in book_comments:
                        book_comments[book_id] = []
                    book_comments[book_id].append({
                        "comment": comment["comments"]
                    })


                response = {
                    "status": "success",
                    "active_books": []
                }
                
                for book in userlibrary:
                    book_id = str(book["book_id"])
                    book_info = await db.ebooks.find_one({"_id": ObjectId(book_id)}, {"_id": 0, "title": 1})
                    if not book_info:
                        continue
                    
                    book_data = {
                        "book_name": book_info["title"],
                        "details": {
                            "collection_date": format_date(book.get("collection_date")),
                            "comments": format_date(book_comments.get(book_id, []))
                            
                        }
                    }

                    response["active_books"].append(book_data)

                self.write(response)
                return

            membership_history = await db.membershiphistory.find({"user_id": ObjectId(user_id)}).to_list(length=None)
            userlibrary = await db.userlibrary.find({"user_id": ObjectId(user_id)}).to_list(length=None)
            comments = await db.feedbacks.find({"user_id": ObjectId(user_id)}).to_list(length=None)

            response = {
                "register_date": format_date(user.get("register_date")),
                "memberships": [],
                "reading_book_history": [],
                "active_books": [],
            }

            for membership in membership_history:
                membership_id = str(membership["membership_id"])
                member_info = await db.membership.find_one({"_id": ObjectId(membership_id)}, {"_id": 0, "type": 1})
                if not member_info:
                    continue
                membership_data = {
                    "membership_type": member_info['type'],
                    "Activation_date": format_date(membership.get("Activation_date")),
                    "End_Date": format_date(membership.get("End_Date")),
                    "isactive": membership.get("isactive")
                }
                response["memberships"].append(membership_data)
                
            book_comments = {}
            for comment in comments:
                book_id = str(comment["book_id"])
                if book_id not in book_comments:
                    book_comments[book_id] = []
                book_comments[book_id].append({
                    "comment": comment["comments"]
                })

            for book in userlibrary:
                book_id = str(book["book_id"])
                book_info = await db.ebooks.find_one({"_id": ObjectId(book_id)}, {"_id": 0, "title": 1})
                if not book_info:
                    continue

                book_data = {
                    "book_name": book_info["title"],
                    "details": {
                        "collection_date": format_date(book.get("collection_date")),
                        "comments": format_date(book_comments.get(book_id, []))
                    }
                }

                if book.get("isactive"):
                    response["active_books"].append(book_data)
                else:
                    response["reading_book_history"].append(book_data)

            self.write({"status": "success", "user": response})

        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
