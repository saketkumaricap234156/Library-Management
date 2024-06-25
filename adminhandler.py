import tornado.web
import json
from db import db
from bson import ObjectId
from db import create_library, create_book, get_libraries_by_admin, get_books_by_manager, get_books_with_managers, get_books_by_library

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")

    def options(self):
        self.set_status(204)
        self.finish()
        
class LibraryHandler(BaseHandler):
    async def post(self):
        try:
            data = json.loads(self.request.body)
            admin_id = data['admin_id']
            name = data['name']
        except (json.JSONDecodeError, KeyError):
            self.set_status(400)
            self.write({'error': 'Invalid request format'})
            return

        library_id = await create_library(admin_id, name)
        self.write({'status': 'success', 'library_id': library_id})

    async def get(self):
        try:
            admin_id = self.get_argument('admin_id')
        except KeyError:
            self.set_status(400)
            self.write({'error': 'Missing admin_id parameter'})
            return

        libraries = await get_libraries_by_admin(admin_id)
        self.write({'status': 'success', 'libraries': libraries})

class BookHandler(tornado.web.RequestHandler):
    async def post(self):
        try:
            data = json.loads(self.request.body)
            manager_id = data.get('manager_id')
            library_id = data.get('library_id ')
            category_id =data.get('category_id')
            title = data.get('title')
            sub_title=data.get('sub_title')
            author = data.get('author')
            description = data.get('description')
            price=data.get('price')
            rating =data.get('rating')
            image_url=data.get('image_url')
             
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
            
        book_id = await create_book(manager_id, library_id , category_id, title, sub_title, author, description, price, rating, image_url)
        if book_id is None:
            self.set_status(400)
            self.write({'error':'Book already exists'})
        else:
         self.write({'status': 'success', 'book_id': book_id})
         
       
    async def get(self):
        try:
            manager_id = self.get_argument('manager_id')
        except KeyError:
            self.set_status(400)
            self.write({'error': 'Missing manager_id parameter'})
            return

        books = await get_books_by_manager(manager_id)
        self.write({'status': 'success', 'books': books})
        
    async def put(self):
        try:
            book_id=self.get_query_argument("book_id")
            data=json.loads(self.request.body)
            category_id=data.get('category_id')
            title=data.get('title')
            sub_title=data.get('sub_title')
            author=data.get('author')
            description=data.get('description')
            price=data.get('price')
            image_url=data.get('image_url')
            
        #     image_data=base64.b64decode(image)
        #     image_filename=data.get('imageFilename', 'uploaded_image')
        #     image_document={
        #     'data':image_data,
        #     'filename':image_filename
        # }
            result = await db.books.update_one(
            {'_id': ObjectId(book_id)},
            {'$set': {'title': title, 'author': author, 'description':description, 'category_id':ObjectId(category_id), 'image_url':image_url, 'sub_title':sub_title, 'price':int(price)}}
        )
            if result.matched_count:
                  self.write({"status": "success", "message": "Book details updated successfully."})
            else:
                self.set_status(404)
                self.write({"status": "error", "message": "Book not found."})
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
            
    async def delete(self):
        try:
            book_id=self.get_query_argument("book_id")
            result = await db.books.delete_one({'_id': ObjectId(book_id)})
            if result.deleted_count == 1:
                self.write({'status': 'success', 'message': 'Book deleted'})
            else:
                self.set_status(404)
                self.write({'status': 'error', 'message': 'Book not found'})
            
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
            
class AdminDetailsHandler(tornado.web.RequestHandler):
    async def get(self):
        try:
            admin_id = self.get_argument('admin_id')
        except KeyError:
            self.set_status(400)
            self.write({'error': 'Missing admin_id parameter'})
            return
        
        books_with_managers = await get_books_with_managers()
        self.write({'status': 'success','books': books_with_managers})    
        
class LibraryBooksHandler(tornado.web.RequestHandler):
    async def get(self):
        try:
            library_id = self.get_argument('library_id')
        except KeyError:
            self.set_status(400)
            self.write({'error': 'Missing manager_id parameter'})
            return

        books = await get_books_by_library(library_id)
        self.write({'status': 'success', 'books': books})
            
            
