import tornado.web
import json
from json import dumps
from db import db
from bson import ObjectId
from tornado.escape import json_encode
from db import create_manager, get_managers_by_library
from RegisterHandler import BaseHandler
class ManagerHandler(BaseHandler):
    async def post(self):
        try:
            data = json.loads(self.request.body)
            library_id = data['library_id']
            profile_url = data.get("profile_url"),
            name = data['name']
            email = data['email']
            mobile = data['mobile']
            password = data['password']
        except (json.JSONDecodeError, KeyError):
            self.set_status(400)
            self.write({'error': 'Invalid request format'})
            return

        manager_id = await create_manager(library_id, profile_url, name, email, mobile, password)
        self.write({'status': 'success', 'manager_id': manager_id})   
        
    async def put(self):
        try:
            manager_id=self.get_argument("manager_id")
            data = json.loads(self.request.body)
            profile_url=data['profile_url']
            name = data['name']
            email = data['email']
            mobile = data['mobile']
        except (json.JSONDecodeError, KeyError):
            self.set_status(400)
            self.write({'error': 'Invalid request format'})
            return

        result = await db.managers.update_one(
            {'_id': ObjectId(manager_id)},
            {'$set': {'name': name, 'profile_url':profile_url, 'email': email, 'mobile': mobile}}
        )

        if result.modified_count == 1:
            self.write({'status': 'success', 'message': 'Manager updated'})
        else:
            self.set_status(404)
            self.write({'status': 'error', 'message': 'Manager not found'})
            
    async def get(self):
        try:
            managers_cursor = db.managers.find({})
            managers = []
            async for manager in managers_cursor:
                managers.append({
                    "_id":str(manager.get("_id")),
                    "name": manager.get("name"),
                    "email": manager.get("email"),
                    "mobile": manager.get("mobile"),
                    "library_id": str(manager.get("library_id")),
                    "profile_url": manager.get("profile_url")
                })
            self.write(dumps(managers))
                
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
                 
    async def delete(self, manager_id):
        result = await db.managers.delete_one({'_id': ObjectId(manager_id)})
        if result.deleted_count == 1:
            self.write({'status': 'success', 'message': 'Manager deleted'})
        else:
            self.set_status(404)
            self.write({'status': 'error', 'message': 'Manager not found'})
            
class LibraryManagersHandler(tornado.web.RequestHandler):
    async def get(self):
        try:
            library_id = self.get_argument('library_id')
        except KeyError:
            self.set_status(400)
            self.write({'error': 'Missing library_id parameter'})
            return

        managers = await get_managers_by_library(library_id)
        self.write({'status': 'success', 'managers': managers})