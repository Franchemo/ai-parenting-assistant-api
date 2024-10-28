import secrets
import base64

def generate_jwt_secret():
    # Generate a 32-byte (256-bit) random secret
    random_bytes = secrets.token_bytes(32)
    
    # Convert to base64 for easier handling
    secret = base64.b64encode(random_bytes).decode('utf-8')
    
    print("\nGenerated JWT Secret:")
    print("---------------------")
    print(secret)
    print("\nAdd this to your Railway environment variables as:")
    print(f"JWT_SECRET={secret}")
    print("\nMake sure to keep this secret secure and don't share it publicly!")

if __name__ == "__main__":
    generate_jwt_secret()
