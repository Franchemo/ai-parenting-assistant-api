import urllib.parse

def format_mongodb_url():
    print("MongoDB Connection String Formatter")
    print("-----------------------------------")
    
    # Get connection details
    username = input("Enter your MongoDB username: ")
    password = input("Enter your MongoDB password: ")
    cluster = input("Enter your cluster address (e.g., cluster0.xxxxx.mongodb.net): ")
    
    # URL encode username and password
    encoded_username = urllib.parse.quote_plus(username)
    encoded_password = urllib.parse.quote_plus(password)
    
    # Format connection string with SSL parameters
    connection_string = (
        f"mongodb+srv://{encoded_username}:{encoded_password}@{cluster}"
        f"/parentassistant?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_REQUIRED"
    )
    
    print("\nFormatted connection string:")
    print(connection_string)
    print("\nAdd this to your .env file as:")
    print(f"MONGODB_URL={connection_string}")

if __name__ == "__main__":
    format_mongodb_url()
