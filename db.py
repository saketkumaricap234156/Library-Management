import motor.motor_tornado
import bcrypt
from bson import ObjectId

# MongoDB connection
client = motor.motor_tornado.MotorClient('mongodb://localhost:27017')
db = client["LibraryManagement"]
fs=motor.motor_tornado.MotorGridFSBucket(db)
# def get_database():
#     return db



def to_json(doc):
    #Convert MongoDB document to JSON-serializable format.
    if isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, bytes):
        return doc.decode('utf-8')   # Convert bytes to string
    elif isinstance(doc, dict):
        # Exclude 'password' field from managers
        if 'password' in doc:
            doc.pop('password')
        return {k: to_json(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [to_json(i) for i in doc]
    return doc

#Query and functions
async def create_library(admin_id, name):
    result = await db.libraries.insert_one({'admin_id': ObjectId(admin_id), 'name': name})
    return str(result.inserted_id)

async def create_book(manager_id, library_id, category_id, title, sub_title, author, description, price, rating, image_url):
    existing_book = await db.books.find_one({'title':title, 'author':author})
    if existing_book:
        return None
    
    result = await db.books.insert_one({'manager_id': ObjectId(manager_id), 'library_id': ObjectId(library_id ), 'category_id':ObjectId(category_id), 'title': title, 'sub_title':sub_title, 'author': author, 'description':description, 'price':int(price), 'rating':rating, 'image_url':image_url})
    return str(result.inserted_id)

async def create_manager(library_id, admin_id, name, email, mobile, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    result = await db.managers.insert_one({
        'admin_id': ObjectId(admin_id),
        'library_id':ObjectId(library_id),
        'name': name,
        'email': email,
        'mobile': mobile,
        'password': hashed_password
    })
    return str(result.inserted_id)

async def get_libraries_by_admin(admin_id):
    libraries = await db.libraries.find({'admin_id': ObjectId(admin_id)}).to_list(length=None)
    return [to_json(library) for library in libraries]

async def get_books_by_manager(manager_id):
    books = await db.books.find({'manager_id': ObjectId(manager_id)}).to_list(length=None)
    return [to_json(book) for book in books]

async def get_managers_by_library(library_id):
    managers = await db.managers.find({'library_id': ObjectId(library_id)}).to_list(length=None)
    return [to_json(manager) for manager in managers]

async def get_books_by_library(library_id):
    books = await db.books.find({'library_id':ObjectId(library_id)}).to_list(length=None)
    return[to_json(book) for book in books]

async def get_books_with_managers():
    books = await db.books.aggregate([
        {
            '$lookup': {
                'from': 'managers',
                'localField': 'manager_id',
                'foreignField': '_id',
                'as': 'manager'
            }
        },
        {
            '$unwind': '$manager'
        }
    ]).to_list(length=None)
    return [to_json(book) for book in books]

async def create_membership(admin_id, type, price, duration_in_months, benefits):
    result= await db.membership.insert_one({'admin_id':ObjectId(admin_id), 'type':type, 'price':int(price),'duration_in_months':int(duration_in_months), 'benefits':benefits })
    return str(result.inserted_id)

async def get_membership(membership_id):
    memberships = await db.membership.find({'_id': ObjectId(membership_id)}).to_list(length=None)
    return [to_json(memberships) for memberships in memberships]
 
async def create_ebook(category_id,  title, sub_title, author, description, price, image_url, rating):
    existing_book = await db.books.find_one({'title':title, 'author':author})
    if existing_book:
        return None
    
    result = await db.ebooks.insert_one({'category_id':ObjectId(category_id),'title': title, 'sub_title':sub_title, 'author': author, 'description':description, 'rating':rating, 'image_url':image_url, 'price':int(price)})
    return str(result.inserted_id)
    
async def get_ebooks(ebook_id):
    return await db.ebooks.find_one({'_id': ObjectId(ebook_id)})

async def get_allebooks():
    return await db.ebooks.find().to_list(length=None)
    # return [to_json(ebook) for ebook in books]

async def create_category(category_name, no_of_books):
    category=await db.category.find_one({'category_name':category_name})
    if category:
        return None
    
    result=await db.category.insert_one({'category_name':category_name, 'no_of_books':int(no_of_books)})
    return str(result.inserted_id)
 