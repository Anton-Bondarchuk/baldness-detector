"""
AppSettings Configuration Data Generator

Run this code to generate secure configuration values for your AppSettings class.
"""

import secrets
import string

# Generate secure secret keys
def generate_secret_key(length=64):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Generate the configuration data
secret_key = generate_secret_key(64)
jwt_secret_key = generate_secret_key(64)

print("🔐 Generated AppSettings Configuration Data")
print("=" * 50)

print("\n📝 Environment Variables for .env file:")
print(f'APP_SECRET_KEY="{secret_key}"')
print(f'APP_DEBUG=false')
print(f'APP_JWT_SECRET_KEY="{jwt_secret_key}"')
print(f'APP_JWT_ALGORITHM=HS256')
print(f'APP_JWT_EXPIRATION_HOURS=24')

print("\n🐍 Python Values:")
print(f"secret_key = '{secret_key}'")
print(f"debug = False")
print(f"jwt_secret_key = '{jwt_secret_key}'")
print(f"jwt_algorithm = 'HS256'")
print(f"jwt_expiration_hours = 24")

print("\n💻 Direct AppSettings Usage:")
print(f"""
from pydantic import SecretStr
from app.config import AppSettings

app_settings = AppSettings(
    secret_key=SecretStr("{secret_key}"),
    debug=False,
    jwt_secret_key=SecretStr("{jwt_secret_key}"),
    jwt_algorithm="HS256",
    jwt_expiration_hours=24
)
""")

print("\n📊 Security Info:")
print(f"Secret key length: {len(secret_key)} characters")
print(f"JWT secret length: {len(jwt_secret_key)} characters")
print("Entropy: High (cryptographically secure)")
print("Algorithm: HS256 (HMAC with SHA-256)")
print("Token lifetime: 24 hours")

print("\n✅ Copy the environment variables to your .env file!")
