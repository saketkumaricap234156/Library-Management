import tornado
import json
from db import db
from bson import ObjectId
from datetime import datetime

class UserlibraryHandler(tornado.web.RequestHandler):
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

            book = await db.ebooks.find_one({"_id": ObjectId(book_id)})
            if not book:
                self.set_status(404)
                self.write({"error": "Book not found"})
                return
            
            existing_book = await db.userlibrary.find_one({"book_id":ObjectId(book_id), "user_id":ObjectId(user_id)})
            if existing_book:
                self.write({'message':"This book is already added in your library"})
            else:
                await db.userlibrary.update_many(
                    {"user_id": ObjectId(user_id), "isactive": True},
                    {"$set": {"isactive": False}}
                )
                collection_date = datetime.now()
                new_book = {
                    "user_id": ObjectId(user_id),
                    "book_id": ObjectId(book_id),
                    "collection_date": collection_date,
                    "isactive": True
                }
                await db.userlibrary.insert_one(new_book)
                            
                self.write({"status": "success", "message": "Book added successfully"})
            
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})   
           
    async def get(self):
        try:
            user_id = self.get_argument('user_id')
            
            user_books_cursor = db.userlibrary.find({'user_id': ObjectId(user_id)})
            user_books = await user_books_cursor.to_list(length=None)
            book_ids = [entry['book_id'] for entry in user_books]
            
            books_cursor = db.ebooks.find({'_id': {'$in': [ObjectId(book_id) for book_id in book_ids]}})
            books = await books_cursor.to_list(length=None)
            
            categorized_books = {}
            for book in books:
                category=await db.category.find_one({'_id':ObjectId(book['category_id'])})
                category_name = category['category_name'] if category else 'Unknown'
                
                filtered_book = {
                'title': book['title'],
                'author': book['author'],
                'description':book['description'],
                'rating':book['rating'],
                'price': book['price']
            }
                if category_name not in categorized_books:
                    categorized_books[category_name] = []
                categorized_books[category_name].append(filtered_book)

            self.write(json.dumps(categorized_books, default=str))
            
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)}) 
            
            
            
               
            
            
            