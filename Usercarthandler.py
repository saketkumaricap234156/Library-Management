import tornado.web
import tornado.ioloop
import json
from bson import ObjectId
from db import db
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
        
class Usercarthandler(BaseHandler):
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

            new_book_entry = {
                "book_id": ObjectId(book_id),
                "collection_date": datetime.now()
            }

            user_cart = await db.usercart.find_one({"user_id": ObjectId(user_id)})

            if user_cart:
                if any(b['book_id'] == ObjectId(book_id) for b in user_cart.get('books', [])):
                    self.write({'message': "This book is already added in your library"})
                    return

                await db.usercart.update_one(
                    {"user_id": ObjectId(user_id)},
                    {"$push": {"books": new_book_entry}}
                )
            else:
                new_cart_entry = {
                    "user_id": ObjectId(user_id),
                    "books": [new_book_entry]
                }
                await db.usercart.insert_one(new_cart_entry)

            self.write({"status": "success", "message": "Book added successfully"})

        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
            
    async def get(self):
        try:
            user_id = self.get_argument('user_id', None)
        
            if not user_id:
                self.set_status(400)
                self.write({"error": "user_id is required"})
                return
        
            # membership = await db.membershiphistory.find_one({"user_id": ObjectId(user_id), "isactive": True})
            # if not membership:
            #     self.set_status(403)
            #     self.write({"error": "You have no active membership to access the books"})
            #     return
            
            user_cart = await db.usercart.find_one({"user_id": ObjectId(user_id)})
            
            if not user_cart or not user_cart.get('books'):
                self.set_status(404)
                self.write({"error": "No books found for this user"})
                return
        
            books_details = []
            for book in user_cart['books']:
                book_id = book['book_id']
                book_details = await db.ebooks.find_one({"_id": ObjectId(book_id)})
                if book_details:
                    books_details.append({
                        "_id":str(book_details.get('_id')),
                        "title": book_details.get('title'),
                        "author": book_details.get('author'),
                        "description":book_details.get('description'),
                        "sub_title": book_details.get('sub_title'),
                        "rating": book_details.get('rating'),
                        "price": book_details.get('price'),
                        "image_url":book_details.get('image_url')
                    })
        
            self.write({"books": books_details})
        
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
            
    async def delete(self):
        try:
            request_data = json.loads(self.request.body.decode('utf-8'))
            user_id = request_data.get('user_id')
            book_id = request_data.get('book_id')
            
            result = await db.usercart.update_one(
                {"user_id": ObjectId(user_id)},
                {"$pull": {"books": {"book_id": ObjectId(book_id)}}}
            )
            
            if result.modified_count:
                self.write({"status": "success", "message": f"Book with id {book_id} removed from cart"})
            else:
                self.write({"status": "error", "message": f"Book with id {book_id} not found in cart"})
                
        except Exception as e:
            self.set_status(400)
            self.write({'error': str(e)})
                
            
class CheckBookHandler(BaseHandler):
    async def post(self):
        try:
                data = json.loads(self.request.body)
                user_id = data.get("user_id")
                book_id = data.get("book_id")
                
                user_cart = await db.usercart.find_one({'user_id': ObjectId(user_id)})
                if user_cart:
                    books = user_cart.get('books', [])
                    book_present = any(book['book_id'] ==ObjectId(book_id) for book in books)
                    self.write({'book_present': book_present})
                else:
                    self.write({'book_present': False})
                    
        except Exception as e:
            self.set_status(400)
            self.write({'error': str(e)})
                
            
        
        
                
        
        

                
            
   
                