import base64
import tornado.web
import json
from db import create_ebook
from db import db, get_ebooks, get_allebooks
from bson import ObjectId

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")

    def options(self):
        self.set_status(204)
        self.finish()

class eBookHandler(BaseHandler):
    async def post(self):
        try:
            data=json.loads(self.request.body)
            # admin_id=data.get('admin_id')
            category_id=data.get('category_id')
            title=data.get('title')
            sub_title=data.get('sub_title')
            author=data.get('author')
            description=data.get('description')
            price=data.get('price')
            rating=data.get('rating')
            image_url=data.get('image_url')
        except (json.JSONDecodeError, KeyError):
            self.set_status(400)
            self.write({'error': 'Invalid request format'})
            return
        
        # image_data=base64.b64decode(image)
        # image_filename=data.get('imageFilename', 'uploaded_image')
        # image_document={
        #     'data':image_data,
        #     'filename':image_filename
        # }
        ebook_id = await create_ebook(category_id, title, sub_title, author, description, price, image_url, rating)
        if ebook_id is None:
             self.set_status(400)
             self.write({'error':'Book already exists'})
        else:
         self.write({'status': 'success', 'ebook_id':ebook_id})
               
    async def put(self):
        try:
            ebook_id=self.get_query_argument("ebook_id")
            data=json.loads(self.request.body)
            # category_id=data.get('category_id')
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
            result = await db.ebooks.update_one(
            {'_id': ObjectId(ebook_id)},
            {'$set': {'title': title, 'author': author, 'description':description, 'image_url':image_url, 'sub_title':sub_title, 'price':int(price)}}
        )
            if result.matched_count:
                  self.write({"status": "success", "message": "eBook details updated successfully."})
            else:
                self.set_status(404)
                self.write({"status": "error", "message": "eBook not found."})
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
        
    async def get(self):
        try:
            categories_cursor = db.category.find()
            categories = {}
            
            async for category in categories_cursor:
                categories[str(category['_id'])] = category['category_name']

            ebooks_cursor = db.ebooks.find()
            category_books = {}
            
            async for ebook in ebooks_cursor:
                category_name = categories.get(str(ebook['category_id']), 'Unknown')
                if category_name not in category_books:
                    category_books[category_name] = []

                category_books[category_name].append({
                    "_id":str(ebook['_id']),
                    'title': ebook['title'],
                    'sub_title': ebook.get('sub_title', ''),
                    'author': ebook['author'],
                    'description':ebook.get('description', ''),
                    'price': ebook['price'],
                    'rating': ebook.get('rating', 0),
                    'image_url':ebook.get('image_url', '')
                })
            self.write(json.dumps(category_books))
            
        except Exception as e:
            self.set_status(500)
            self.write({'error': str(e)})
       
    async def delete(self):
        try:
            ebook_id=self.get_argument('ebook_id')
            result = await db.ebooks.delete_one({'_id': ObjectId(ebook_id)})
            if result.deleted_count:
                self.write({'status': 'success', 'message': 'eBook deleted'})
            else:
                self.set_status(404)
                self.write({'status': 'error', 'message': 'eBook not found'})
                
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
       
                
            