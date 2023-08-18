import secrets

print("secret key:", secrets.token_urlsafe(32))
print("secret hash:", secrets.token_urlsafe(16))