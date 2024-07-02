import tornado.ioloop
import tornado.web
from bson import ObjectId
import json
from db import db

class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.body:
            try:
                self.json_args = tornado.escape.json_decode(self.request.body)
            except json.JSONDecodeError:
                self.json_args = {}
        else:
            self.json_args = {}
            
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()
    
class UserBooksHandler(BaseHandler):
    async def get(self):
        try:
            title = self.get_argument('title', None)
            author = self.get_argument('author', None)
            category=self.get_argument('category', None)
        
            query = {}
            projection = {'title': 1, 'author': 1, 'rating':1, 'description':1, '_id': 0}
            if title:
                query['title'] = {'$regex': title, '$options': 'i'}
            if author:
                query['author'] = {'$regex': author, '$options': 'i'} 
            if category:
                category_doc = await db.category.find_one({'category_name': {'$regex': category, '$options': 'i'}})
                if category_doc:
                    query['category_id'] = category_doc['_id']
                else:
                    self.set_status(404)
                    self.write({'message': 'Category not found'})
                    return 
                books = await db.books.find(query, projection).to_list(length=None)
            if books:
                self.write({'status': 'success', 'books':books})
            else:
                self.set_status(404)
                self.write({'message':'No Books Found'})
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})
            
class UsereBooksHandler(BaseHandler):
    async def get(self):
        try:
            title = self.get_argument('title', None)
            author = self.get_argument('author', None)
            category=self.get_argument('category', None)
            
            query = {}
            projection = {'title': 1, 'sub_title':1, 'author': 1, 'rating':1, 'description':1, 'price':1, 'image_url':1, '_id': 1}
                
            if title:
                query['title'] = {'$regex': title, '$options': 'i'}
            if author:
                query['author'] = {'$regex': author, '$options': 'i'}
            if category:
                category_doc = await db.category.find_one({'category_name': {'$regex': category, '$options': 'i'}})
                if category_doc:
                    query['category_id'] = category_doc['_id']
                else:
                    self.set_status(404)
                    self.write({'message': 'Category not found'})
                    return    
            books = await db.ebooks.find(query, projection).to_list(length=None)
            if books:
                for book in books:
                    book['_id'] = str(book['_id'])
                    if 'category_id' in book and isinstance(book['category_id'], ObjectId):
                        book['category_id'] = str(book['category_id'])
                self.write({'status': 'success', 'books': books})
            else:
                self.set_status(404)
                self.write({'message':'No Books Found'})
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})
  
class UsereBooksHandlerbyid(BaseHandler):
    async def get(self):
        try:
            book_id=self.get_argument('book_id')
            
            book = await db.ebooks.find_one({"_id":ObjectId(book_id)})
            if book:
                self.write({
                    "_id":str(book.get("_id")),
                    "title": book.get("title"),
                    "sub_title": book.get("sub_title"),
                    "author": book.get("author"),
                    "rating": book.get("rating"),
                    "description":book.get("description"),
                    "price":book.get("price"),
                    "image_url":book.get("image_url")
                    
                })
            else:
                self.set_status(404)
                self.write({"error": "Book not found"})    
                
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})
                 