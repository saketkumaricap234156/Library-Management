import tornado
import json
from db import create_category, db
from bson import ObjectId

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()


class CategoryHandler(BaseHandler):
    async def post(self):
        try:
            data=json.loads(self.request.body)
            category_name=data.get('category_name')
            no_of_books=data.get('no_of_books')
            
            category_id= await create_category(category_name, no_of_books)
            if category_id is None:
                 self.set_status(400)
                 self.write({'error':'Category already exists'})
            else:
                self.write({'status': 'success', 'category_id':category_id})
                
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
        
    async def put(self):
        try:
            category_id=self.get_argument('category_id')
            data=json.loads(self.request.body)
            category_name=data.get('category_name')
            no_of_books=data.get('no_of_books')
        
            result=await db.category.update_one(
             {'_id': ObjectId(category_id)},
            {'$set': {'category_name': category_name, 'no_of_books': int(no_of_books)}}
        )
        
            if result.matched_count:
                  self.write({"status": "success", "message": "Category details updated successfully."})
            else:
                self.set_status(404)
                self.write({"status": "error", "message": "Category not found."})
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
            
    async def delete(self):
        try:
            category_id=self.get_argument('category_id')
        
            result = await db.category.delete_one({'_id': ObjectId(category_id)})
            if result.deleted_count:
                self.write({'status': 'success', 'message': 'Category deleted'})
            else:
                self.set_status(404)
                self.write({'status': 'error', 'message': 'Category not found'})
                
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
    
    async def get(self):
        try:
            excluded_categories = ["Popular Books", "Best Seller", "Recommended", "Featured Books"]
            cursor = db.category.find({"category_name": {"$nin": excluded_categories}}, {"_id": 0, "category_name": 1})
            category_names = []
            async for document in cursor:
                category_names.append(document["category_name"])
            
            self.write(json.dumps(category_names))
            
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})
   
            
            
                     
                 
            
                     
         
        
            