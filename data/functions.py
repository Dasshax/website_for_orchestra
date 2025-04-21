import hashlib
import re


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_password(password, hashed_password):
    return hash_password(password) == hashed_password