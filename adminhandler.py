import tornado.web
import json
from db import db
from bson import ObjectId
from db import create_library, create_book, get_libraries_by_admin, get_books_by_id, get_books_with_managers, get_books_by_library

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

class BookHandler(BaseHandler):
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
            book_id = self.get_argument('book_id')
        
            if book_id:
                books = await get_books_by_id(book_id)
                self.write({'status': 'success', 'books': books})
                  
        except Exception as e:
            self.set_status(500)
            self.write({'error': str(e)})
        
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
            
class Getallbookhandler(BaseHandler):
    async def get(self):
        try:
                categories_cursor = db.category.find()
                categories = {}
                
                async for category in categories_cursor:
                    categories[str(category['_id'])] = category['category_name']

                ebooks_cursor = db.books.find()
                category_books = {}
                
                async for book in ebooks_cursor:
                    category_name = categories.get(str(book['category_id']), 'Unknown')
                    if category_name not in category_books:
                        category_books[category_name] = []

                    category_books[category_name].append({
                        "_id":str(book['_id']),
                        'title': book['title'],
                        'sub_title': book.get('sub_title', ''),
                        'author': book['author'],
                        'description':book.get('description', ''),
                        'price': book['price'],
                        'rating': book.get('rating', 0),
                        'image_url':book.get('image_url', '')
                    })
                self.write(json.dumps(category_books))
                
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
                
            
class AdminDetailsHandler(BaseHandler):
    async def get(self):
        try:
            admin_id = self.get_argument('admin_id')
        except KeyError:
            self.set_status(400)
            self.write({'error': 'Missing admin_id parameter'})
            return
        
        books_with_managers = await get_books_with_managers()
        self.write({'status': 'success','books': books_with_managers})    
        
class LibraryBooksHandler(BaseHandler):
    async def get(self):
        try:
            library_id = self.get_argument('library_id')
        except KeyError:
            self.set_status(400)
            self.write({'error': 'Missing manager_id parameter'})
            return

        books = await get_books_by_library(library_id)
        self.write({'status': 'success', 'books': books})
        
class Userdeatailshandler(BaseHandler):
    async def get(self):
        try:
            users = await db.users.find({}, {'_id':1, 'name': 1, 'mobile': 1, 'email': 1, 'register_date':1, 'profile_url':1}).to_list(length=None)

            if not users:
                self.set_status(404)
                self.write({"error": "No users found"})
                return

            all_user_details = []

            for user in users:
                user_id = user['_id']

                membership_histories = await db.membershiphistory.find(
                    {'user_id': ObjectId(user_id)},
                    {'membership_id': 1, 'Activation_date': 1, 'End_Date': 1, 'isactive': 1}
                ).to_list(length=None)

                membership_details_list = []
                for history in membership_histories:
                    membership = await db.membership.find_one(
                        {'_id': history['membership_id']},
                        {'type': 1, 'duration_in_months': 1, 'price': 1}
                    )

                    if membership:
                        membership_details = {
                            "type": membership['type'],
                            "duration_in_months": membership['duration_in_months'],
                            "price": membership['price'],
                            "Activation_date": history['Activation_date'].strftime('%Y-%m-%d') if history['Activation_date'] else None,
                            "End_Date": history['End_Date'].strftime('%Y-%m-%d') if history['End_Date'] else None,
                            "isactive": history['isactive']
                        }
                        membership_details_list.append(membership_details)

                user_details = {
                    "_id":str(user['_id']),
                    "name": user['name'],
                    "mobile": user['mobile'],
                    "email": user['email'],
                    "register_date":user['register_date'].strftime('%Y-%m-%d') if user['register_date'] else None,
                    "profile_url":user['profile_url'],
                    "memberships": membership_details_list
                }

                all_user_details.append(user_details)

            self.write({"users": all_user_details})

        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
            
class Fetchuserbyid(BaseHandler):
    async def get(self):
        try:
            user_id = self.get_argument('user_id')

            user = await db.users.find_one(
                {'_id': ObjectId(user_id)},
                {'_id': 1, 'name': 1, 'mobile': 1, 'email': 1, 'register_date': 1, 'profile_url': 1}
            )

            if not user:
                self.set_status(404)
                self.write({"error": "User not found"})
                return

            membership_history = await db.membershiphistory.find_one(
                {'user_id': ObjectId(user_id)},
                {'membership_id': 1, 'Activation_date': 1, 'End_Date': 1, 'isactive': 1}
            )

            if membership_history:
                if membership_history['isactive']:
                    membership = await db.membership.find_one(
                        {'_id': membership_history['membership_id']},
                        {'type': 1, 'duration_in_months': 1, 'price': 1}
                    )

                    if membership:
                        membership_details = {
                            "type": membership['type'],
                            "duration_in_months": membership['duration_in_months'],
                            "price": membership['price'],
                            "Activation_date": membership_history['Activation_date'].strftime('%Y-%m-%d') if membership_history['Activation_date'] else None,
                            "End_Date": membership_history['End_Date'].strftime('%Y-%m-%d') if membership_history['End_Date'] else None,
                            "isactive": membership_history['isactive']
                        }
                    else:
                        membership_details = {"error": "Membership type not found"}
                else:
                    membership_details = {}
            else:
                membership_details = {}

            rented_book = await db.rentedhistory.find_one({"user_id": ObjectId(user_id)})

            reading_book_history = []
            active_books = []

            if rented_book:
                for book_entry in rented_book["books"]:
                    book_id = book_entry["book_id"]
                    book = await db.books.find_one(
                        {"_id": ObjectId(book_id)}, 
                        {"_id": 1, "title": 1, "sub_title": 1, "price": 1, "rating": 1, "author": 1, "image_url":1, "description":1}
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
                        "image_url":book.get("image_url"),
                        "rented_date": book_entry["rented_date"].strftime('%Y-%m-%d') if book_entry["rented_date"] else None
                    }

                    if book_entry["return_status"]:
                        active_books.append(book_data)
                    else:
                        reading_book_history.append(book_data)

            user_details = {
                "_id": str(user['_id']),
                "name": user['name'],
                "mobile": user['mobile'],
                "email": user['email'],
                "register_date": user['register_date'].strftime('%Y-%m-%d') if user['register_date'] else None,
                "profile_url": str(user['profile_url']),
                "membership": membership_details,
                "reading_book_history": reading_book_history,
                "active_books": active_books
            }

            self.write(user_details)

        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
    
                

    
            
            
            
            
