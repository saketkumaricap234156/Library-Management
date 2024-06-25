import tornado
from db import db
from bson import ObjectId
import json
from json import dumps

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

def convert_to_serializable(data):
    if isinstance(data, list):
        return [convert_to_serializable(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_to_serializable(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

class CategoriesHandler(BaseHandler):
    async def get(self):
            try:
                fetch_type = self.get_argument('fetch', 'all')
                if fetch_type=="ebooks":
                    ebooks_pipeline = [
                    {
                        "$lookup": {
                            "from": "ebooks",
                            "localField": "_id",
                            "foreignField": "category_id",
                            "as": "items"
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "category_name": "$category_name",
                            "items": {
                                "$map": {
                                    "input": "$items",
                                    "as": "item",
                                    "in": {
                                        # "_id": "$$item._id",
                                        "title": "$$item.title",
                                        "sub_title":"$$item.sub_title",
                                        "author": "$$item.author",
                                        "description": "$$item.description",
                                        "rating": "$$item.rating",
                                        "price": "$$item.price"
                                    }
                                }
                            }
                        }
                    },
                    {
                        "$addFields": {
                            "items": {
                                "$cond": {
                                    "if": { "$eq": [ { "$size": "$items" }, 0 ] },
                                    "then": [],
                                    "else": "$items"
                                }
                            }
                        }
                    }
                ]
                    ebooks_aggregation = await db.category.aggregate(ebooks_pipeline).to_list(None)
                    
                    ebooks_list = []
                    ebooks_list.extend(convert_to_serializable(ebooks_aggregation))
                    
                    result = {
                    "books": [
                        {"ebooks": ebooks_list}
                    ]
                }
                    
                    self.write(result)
                    
                elif fetch_type=="books":
                    books_pipeline = [
                        {
                            "$lookup": {
                                "from": "books",
                                "localField": "_id",
                                "foreignField": "category_id",
                                "as": "items"
                            }
                        },
                        {
                            "$project": {
                                "_id": 0,
                                "category_name": "$category_name",
                                "items": {
                                    "$map": {
                                        "input": "$items",
                                        "as": "item",
                                        "in": {
                                            # "_id": "$$item._id",
                                            "title": "$$item.title",
                                            "sub_title":"$$item.sub_title",
                                            "author": "$$item.author",
                                            "description": "$$item.description",
                                            "rating": "$$item.rating",
                                            "price": "$$item.price"
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "$addFields": {
                                "items": {
                                    "$cond": {
                                        "if": { "$eq": [ { "$size": "$items" }, 0 ] },
                                        "then": [],
                                        "else": "$items"
                                    }
                                }
                            }
                        }
                    ]
                    
                    books_aggregation = await db.category.aggregate(books_pipeline).to_list(None)
                    books_list = []
                    books_list.extend(convert_to_serializable(books_aggregation))
                    
                    result = {
                        "books": [
                            {"physical_books": books_list}
                        ]
                    } 
                    self.write(result)
                    
            
                elif fetch_type == "category":
                    category_name = self.get_argument('category_name')
                    
                    ebooks_pipeline = [
                        {"$match": {"category_name": category_name}},
                        {"$lookup": {
                            "from": "ebooks",
                            "localField": "_id",
                            "foreignField": "category_id",
                            "as": "items"
                        }},
                        {"$project": {
                            "_id": 0,
                            "category_name": 1,
                            "items": {
                                "$map": {
                                    "input": "$items",
                                    "as": "item",
                                    "in": {
                                        "title": "$$item.title",
                                        "sub_title": "$$item.sub_title",
                                        "author": "$$item.author",
                                        "description": "$$item.description",
                                        "rating": "$$item.rating",
                                        "price": "$$item.price"
                                    }
                                }
                            }
                        }},
                        {"$addFields": {
                            "items": {
                                "$cond": {
                                    "if": {"$eq": [{"$size": "$items"}, 0]},
                                    "then": [],
                                    "else": "$items"
                                }
                            }
                        }}
                    ]
                    
                    books_pipeline = [
                        {"$match": {"category_name": category_name}},
                        {"$lookup": {
                            "from": "books",
                            "localField": "_id",
                            "foreignField": "category_id",
                            "as": "items"
                        }},
                        {"$project": {
                            "_id": 0,
                            "category_name": 1,
                            "items": {
                                "$map": {
                                    "input": "$items",
                                    "as": "item",
                                    "in": {
                                        "title": "$$item.title",
                                        "sub_title": "$$item.sub_title",
                                        "author": "$$item.author",
                                        "description": "$$item.description",
                                        "rating": "$$item.rating",
                                        "price": "$$item.price"
                                    }
                                }
                            }
                        }},
                        {"$addFields": {
                            "items": {
                                "$cond": {
                                    "if": {"$eq": [{"$size": "$items"}, 0]},
                                    "then": [],
                                    "else": "$items"
                                }
                            }
                        }}
                    ]
                    
                    ebooks_aggregation = await db.category.aggregate(ebooks_pipeline).to_list(None)
                    books_aggregation = await db.category.aggregate(books_pipeline).to_list(None)
                    
                    ebooks_list = convert_to_serializable(ebooks_aggregation)
                    books_list = convert_to_serializable(books_aggregation)
                    
                    result = {
                        "books": [
                            {"ebooks": ebooks_list},
                            {"physical_books": books_list}
                        ]
                    }
                
                    self.write(result)
                       
                else:
                    ebooks_pipeline = [
                        {
                            "$lookup": {
                                "from": "ebooks",
                                "localField": "_id",
                                "foreignField": "category_id",
                                "as": "items"
                            }
                        },
                        {
                            "$project": {
                                "_id": 0,
                                "category_name": "$category_name",
                                "items": {
                                    "$map": {
                                        "input": "$items",
                                        "as": "item",
                                        "in": {
                                            # "_id": "$$item._id",
                                            "title": "$$item.title",
                                            "sub_title":"$$item.sub_title",
                                            "author": "$$item.author",
                                            "description": "$$item.description",
                                            "rating": "$$item.rating",
                                            "price": "$$item.price"
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "$addFields": {
                                "items": {
                                    "$cond": {
                                        "if": { "$eq": [ { "$size": "$items" }, 0 ] },
                                        "then": [],
                                        "else": "$items"
                                    }
                                }
                            }
                        }
                    ]

                    books_pipeline = [
                        {
                            "$lookup": {
                                "from": "books",
                                "localField": "_id",
                                "foreignField": "category_id",
                                "as": "items"
                            }
                        },
                        {
                            "$project": {
                                "_id": 0,
                                "category_name": "$category_name",
                                "items": {
                                    "$map": {
                                        "input": "$items",
                                        "as": "item",
                                        "in": {
                                            # "_id": "$$item._id",
                                            "title": "$$item.title",
                                            "sub_title":"$$item.sub_title",
                                            "author": "$$item.author",
                                            "description": "$$item.description",
                                            "rating": "$$item.rating",
                                            "price": "$$item.price"
                                        }
                                    }
                                }
                            }
                        },
                        {
                            "$addFields": {
                                "items": {
                                    "$cond": {
                                        "if": { "$eq": [ { "$size": "$items" }, 0 ] },
                                        "then": [],
                                        "else": "$items"
                                    }
                                }
                            }
                        }
                    ]

                    ebooks_aggregation = await db.category.aggregate(ebooks_pipeline).to_list(None)
                    books_aggregation = await db.category.aggregate(books_pipeline).to_list(None)
                    
                    ebooks_list = []
                    books_list = []
                    

                    ebooks_list.extend(convert_to_serializable(ebooks_aggregation))
                    books_list.extend(convert_to_serializable(books_aggregation))

                    result = {
                        "books": [
                            {"ebooks": ebooks_list},
                            {"physical_books": books_list}
                        ]
                    }
                    
                    self.write(result)
            
            except Exception as e:
                self.set_status(500)
                self.write({"status": "error", "message": str(e)})