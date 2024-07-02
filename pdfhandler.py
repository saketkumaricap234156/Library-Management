import tornado.web
import tornado.ioloop
import json
from db import db
from bson import ObjectId
from tornado.escape import json_encode, json_decode
from RegisterHandler import BaseHandler

class Pdfhandler(BaseHandler):
    async def post(self):
        try:
            book_id = self.get_body_argument("book_id")
            fileinfo = self.request.files['pdf'][0]
            filename = fileinfo['filename']
            content_type = fileinfo['content_type']
            filebody = fileinfo['body']
            
            result = await db.bookpdf.insert_one({
                "book_id":ObjectId(book_id),
                "filename": filename,
                "content_type": content_type,
                "filebody": filebody
            })

            self.write(json_encode({
                "message": "PDF uploaded successfully",
                "id": str(result.inserted_id)
            }))
            
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
            
    async def get(self):
        try:
            book_id=self.get_argument('book_id')
            pdf_doc = await db.bookpdf.find_one({"book_id": ObjectId(book_id)})
            
            if not pdf_doc:
                self.set_status(404)
                self.write(json_encode({"error": "PDF not found"}))
                return

            self.set_header('Content-Type', pdf_doc['content_type'])
            self.set_header('Content-Disposition', f'attachment; filename={pdf_doc["filename"]}')
            
            print("******************")
            self.write(pdf_doc['filebody'])
            
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
            
    async def put(self):
        try:
            book_id = self.get_body_argument("book_id")

            fileinfo = self.request.files['pdf'][0]
            filename = fileinfo['filename']
            content_type = fileinfo['content_type']
            filebody = fileinfo['body']

            result = await db.bookpdf.update_one(
                {"book_id": ObjectId(book_id)},
                {"$set": {
                    "filename": filename,
                    "content_type": content_type,
                    "filebody": filebody
                }}
            )

            if result.matched_count == 0:
                self.set_status(404)
                self.write(json_encode({"error": "PDF not found"}))
            else:
                self.write(json_encode({
                    "message": "PDF updated successfully",
                    "modified_count": result.modified_count
                }))
                
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
            
class GetPDFwithMembershipCheckHandler(BaseHandler):
    async def get(self):
        try:
            data=json.loads(self.request.body)
            user_id=data.get('user_id')
            book_id=data.get('book_id')
            membership = await db.membershiphistory.find_one({"user_id": ObjectId(user_id)})
            
            if not membership:
                self.set_status(403)
                self.write(json_encode({"error": "User does not have a valid membership"}))
                return

            user_cart = await db.usercart.find_one({"user_id": ObjectId(user_id), "books.book_id": ObjectId(book_id)})
            
            if not user_cart:
                self.set_status(404)
                self.write(json_encode({"error": "Book not found in user's cart"}))
                return

            pdf_doc = await db.bookpdf.find_one({"book_id": ObjectId(book_id)})
            
            if not pdf_doc:
                self.set_status(404)
                self.write(json_encode({"error": "PDF not found"}))
                return

            self.set_header('Content-Type', pdf_doc['content_type'])
            self.set_header('Content-Disposition', f'attachment; filename={pdf_doc["filename"]}')
            
            self.write(pdf_doc['filebody'])
            
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})
            
            
            
            
            
                    
                
                
                
            

            
            
            
            