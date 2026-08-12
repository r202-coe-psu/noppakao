APP_TITLE = "COE CTF"
MONGODB_DB = "noppakaodb"
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
SECRET_KEY = "noppakao-secretkey"

OAUTH_CACHE_TYPE = "simple"
CACHE_TYPE = "SimpleCache"
NOPPHAKAO_CACHE_DIR = "/tmp/noppakao/cache"

LOGIN_PROVIDERS = ["PSU", "GOOGLE"]
AUTHLIB_SSL_VERIFY_PSU = False

GOOGLE_CLIENT_ID = ""
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_SECRET = ""
GOOGLE_BASE_URL = "https://www.googleapis.com/oauth2/v1"
GOOGLE_SERVER_METADATA_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_CLIENT_KWARGS = {"scope": "openid profile email"}

