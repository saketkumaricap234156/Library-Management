import tornado.ioloop
import tornado.web

from RegisterHandler import RegisterHandler
from LoginHandler import LoginHandler
from emailauth import AdminGenerateOtpHandler, AdminLoginHandler
from adminhandler import LibraryHandler, BookHandler, AdminDetailsHandler, LibraryBooksHandler
from managerhandler import LibraryManagersHandler, ManagerHandler
from membership import Membershiphandler
from userbookshandler import UserBooksHandler, UsereBooksHandler, UsereBooksHandlerbyid
from usermembership import UserMembershipHandler
from ebookhandler import eBookHandler
from ratinghandler import RatingHandler
from userlibrary import UserlibraryHandler
from categoryhandler import CategoryHandler
from bookwithcategory import CategoriesHandler
from membershiphistory import MembershipHistoryhandler
from userprofile import UserHandler
from Usercarthandler import Usercarthandler, CheckBookHandler

def make_app():
    return tornado.web.Application([
        (r"/register", RegisterHandler),
        (r"/login", LoginHandler),
        (r"/generate-otp", AdminGenerateOtpHandler),
        (r"/emaillogin", AdminLoginHandler),
        (r"/category", CategoryHandler),
        (r"/libraries", LibraryHandler),
        (r"/books", BookHandler),
        (r"/managers", ManagerHandler),
        (r"/manager/books", AdminDetailsHandler),
        (r"/library/managers", LibraryManagersHandler),
        (r"/library/books", LibraryBooksHandler),
        (r"/membership", Membershiphandler),
        (r"/getbooks", UserBooksHandler),
        (r"/buy_membership",UserMembershipHandler),
        (r"/ebook", eBookHandler),
        (r"/getebooks", UsereBooksHandler),
        (r"/rating", RatingHandler),
        (r"/userlibrary", UserlibraryHandler),
        (r"/category/books",CategoriesHandler),
        (r"/user/membership",MembershipHistoryhandler),
        (r"/user_profile",UserHandler),
        (r"/user_cart",Usercarthandler),
        (r"/fetchbook",UsereBooksHandlerbyid),
        (r"/checkbook",CheckBookHandler),
        
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Server running on http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()


