import tornado.web
import tornado.ioloop
import json
from db import db
from bson import ObjectId
from datetime import datetime, timedelta
from RegisterHandler import BaseHandler

class Rentbookhandler(BaseHandler):
    async def post(self):
        try:
            data = json.loads(self.request.body)
            user_id = data.get("user_id")
            book_id = data.get("book_id")
            
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                self.set_status(404)
                self.write({"error": "User not found"})
                return

            book = await db.books.find_one({"_id": ObjectId(book_id)})
            if not book:
                self.set_status(404)
                self.write({"error": "Book not found"})
                return    

            new_book_entry = {
                "book_id": ObjectId(book_id),
                "rented_date": datetime.now(),
                "return_status":False
            }

            rented_book = await db.rentedhistory.find_one({"user_id": ObjectId(user_id)})

            if rented_book:
                if any(b['book_id'] == ObjectId(book_id) for b in rented_book.get('books', [])):
                    self.write({'message': "This book is already rented for you."})
                    return

                await db.rentedhistory.update_one(
                    {"user_id": ObjectId(user_id)},
                    {"$push": {"books": new_book_entry}}
                )
            else:
                new_book_entry = {
                    "user_id": ObjectId(user_id),
                    "books": [new_book_entry]
                }
                await db.rentedhistory.insert_one(new_book_entry)

            self.write({"status": "success", "message": "Book Rented successfully"})

        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
            
    async def put(self):
        try:
            data = json.loads(self.request.body)
            user_id = data.get("user_id")
            book_id = data.get("book_id")
            
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                self.set_status(404)
                self.write({"error": "User not found"})
                return

            book = await db.books.find_one({"_id": ObjectId(book_id)})
            if not book:
                self.set_status(404)
                self.write({"error": "Book not found"})
                return

            rented_book = await db.rentedhistory.find_one(
                {"user_id": ObjectId(user_id), "books.book_id": ObjectId(book_id)}
            )

            if not rented_book:
                self.set_status(404)
                self.write({"error": "Book not rented by user"})
                return

            books = rented_book.get("books", [])
            for b in books:
                if b["book_id"] == ObjectId(book_id):
                    if b.get("return_status"):
                        self.write({"message": "Book already returned"})
                        return

                    b["return_status"] = True
                    b["return_date"] = datetime.now()

            await db.rentedhistory.update_one(
                {"user_id": ObjectId(user_id), "books.book_id": ObjectId(book_id)},
                {"$set": {"books.$": b}}
            )

            self.write({"status": "success", "message": "Book returned successfully"})

        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
            
    async def get(self):
        try:
            rented_books = await db.rentedhistory.find().to_list(None)

            if not rented_books:
                self.set_status(404)
                self.write({"error": "No rental records found"})
                return

            response = []

            for rented_book in rented_books:
                user_id = rented_book["user_id"]
                user = await db.users.find_one({"_id": ObjectId(user_id)}, {"_id": 0, "name": 1})
                if not user:
                    continue

                user_data = {
                    "user_name": user["name"],
                    "books": []
                }

                for book_entry in rented_book["books"]:
                    book_id = book_entry["book_id"]
                    book = await db.books.find_one({"_id": ObjectId(book_id)}, {"_id": 0, "title": 1})
                    if not book:
                        continue

                    book_data = {
                        "book_name": book["title"],
                        "rented_date": book_entry["rented_date"].strftime('%Y-%m-%d') if book_entry["rented_date"] else None ,
                        "return_status": book_entry["return_status"],
                        "return_date": book_entry.get("return_date").strftime('%Y-%m-%d') if book_entry.get("return_date") else None if book_entry.get("return_date") else None
                    }
                    
                    user_data["books"].append(book_data)

                response.append(user_data)

            self.write({"status": "success", "data": response})

        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
                              
class GetUserUnreturnedBooksHandler(BaseHandler):
    async def get(self):
        try:
            user_id = self.get_argument("user_id", None)
            if not user_id:
                self.set_status(400)
                self.write({"error": "user_id is required"})
                return

            rented_book = await db.rentedhistory.find_one(
                {"user_id": ObjectId(user_id)}
            )

            if not rented_book:
                self.set_status(404)
                self.write({"error": "No rental records found for the user"})
                return

            user = await db.users.find_one({"_id": ObjectId(user_id)}, {"_id": 0, "name": 1})
            if not user:
                self.set_status(404)
                self.write({"error": "User not found"})
                return

            user_data = {
                "user_name": user["name"],
                "books": [],
                "reading_book_history":[],
                "active_books":[]
            }

            for book_entry in rented_book["books"]:
                    book_id = book_entry["book_id"]
                    book = await db.books.find_one(
                        {"_id": ObjectId(book_id)}, 
                        {"_id": 1, "title": 1, "sub_title": 1, "image_url":1, "description":1, "price": 1, "rating": 1, "author": 1}
                    )
                    if not book:
                        continue

                    book_data = {
                        "_id":str(book["_id"]),
                        "title": book["title"],
                        "sub_title": book.get("sub_title"),
                        "price": book.get("price"),
                        "rating": book.get("rating"),
                        "author": book.get("author"),
                        "description":book.get("description"),
                        "image_url":book.get("image_url")
                    }

                    user_data["books"].append(book_data)
                    
                    if book_entry["return_status"]:
                        user_data["active_books"].append(book_data)
                    else:
                        user_data["reading_book_history"].append(book_data)

            self.write({"status": "success", "data": user_data})

        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})


            
            
    