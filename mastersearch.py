import re
import tornado.web
import tornado.ioloop
import json
from db import db
from bson import json_util, ObjectId
from RegisterHandler import BaseHandler
class Searchhandler(BaseHandler):
    async def get(self):
        try:
            data=json.loads(self.request.body)
            title=data.get('title',"")
            sub_title=data.get('sub_title',"")
            author=data.get('author',"")
            category=data.get('category',"")
            
            pipeline=[
                {
                    '$lookup': {
                        'from': 'category', 
                        'localField': 'category_id', 
                        'foreignField': '_id', 
                        'as': 'category'
                    }
                }, {
                    '$unwind': '$category'
                }, {
                    '$match': {
                        '$and': [
                            {
                                'title': {
                                    '$regex': title, 
                                    '$options': 'ism'
                                }
                            }, {
                                'author': {
                                    '$regex': author, 
                                    '$options': 'ism'
                                }
                            }, {
                                'sub_title': {
                                    '$regex': sub_title, 
                                    '$options': 'ism'
                                }
                            }, {
                                'category.category_name': {
                                    '$regex': category, 
                                    '$options': 'ism'
                                }
                            }
                        ]
                    }
                }, {
                    '$project': {
                        '_id': 0, 
                        'admin_id': 0, 
                        'category_id': 0, 
                        'category': 0
                    }
                }
            ]
            cursor = db.ebooks.aggregate(pipeline)
            result = await cursor.to_list(length=None)
            self.set_status(200)
            self.write({"status": "success", "data": result})

        except Exception as e:
            self.write({"status": "error", "message": str(e)})
            
class OneSearchHandler(BaseHandler):
    async def post(self):
        try:
            search_query = json.loads(self.request.body)
            search_text = search_query.get('query', '')

            if not search_text:
                self.set_status(400)
                self.write({"status": "error", "message": "Query parameter 'query' is required"})
                return

            regex = re.compile(f".*{search_text}.*", re.IGNORECASE)
            
            category_filter = {"category_name": regex}
            category_projection = {"_id": 1}
            category_cursor = db.category.find(category_filter, category_projection)
            
            category_ids = []
            async for document in category_cursor:
                category_ids.append(document['_id'])

            search_filter = {
                "$or": [
                    {"title": regex},
                    {"sub_title": regex},
                    {"author": regex},
                    {"category_id": {"$in": category_ids}}
                ]
            }

            projection = {"_id": 0, "category_id": 0, "admin_id": 0}

            cursor = db.ebooks.find(search_filter, projection)

            ebooks = []
            async for document in cursor:
                ebooks.append(document)

            self.set_header("Content-Type", "application/json")
            self.write(json.dumps({"status": "success", "data": ebooks}, default=json_util.default))
            
        except Exception as e:
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps({"status": "error", "message": str(e)}))
           