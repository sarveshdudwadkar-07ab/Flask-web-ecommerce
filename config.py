class Config:
    # CRITICAL: Change this to a secure, long, random key!
    SECRET_KEY = 'your_super_secure_secret_key'
    
    # Your updated MySQL connection string
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://flaskuser:flaskpass@localhost/ecommerce_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False