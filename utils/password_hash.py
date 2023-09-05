import hashlib
def get_password_hash(passwordk, salt):
    string_to_hash = passwordk+"+"+salt
    hash_object = hashlib.sha256(string_to_hash.encode())
    return hash_object.hexdigest()