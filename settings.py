import os
import binascii

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'aryanasa893@gmail.com'
EMAIL_PASSWORD = 'pvtd iucf cbev wite'
secret_key = binascii.hexlify(os.urandom(24)).decode()
SECRET_KEY = 'secret_key'




