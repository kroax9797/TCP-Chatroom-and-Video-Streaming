import rsa

def rsa_encrypt(msg , public_key):
    return rsa.encrypt(msg.encode() , public_key)

def rsa_decrypt(msg , private_key):
    return rsa.decrypt(msg , private_key).decode()
