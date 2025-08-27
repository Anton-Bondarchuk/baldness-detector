#!/usr/bin/env python3
"""
Quick AppSettings Configuration Generator

This script generates the exact configuration data needed for the AppSettings class
and shows you how to use it.
"""

import secrets
import string

def generate_secure_key(length=64):
    """Generate a cryptographically secure key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_app_settings_config():
    """Generate configuration data for AppSettings class"""
    
    config = {
        "secret_key": generate_secure_key(64),
        "debug": False,
        "jwt_secret_key": generate_secure_key(64), 
        "jwt_algorithm": "HS256",
        "jwt_expiration_hours": 24
    }
    
    return config

def create_env_variables(config):
    """Create environment variables for the configuration"""
    env_vars = []
    env_vars.append("# AppSettings Configuration")
    env_vars.append(f'APP_SECRET_KEY="{config["secret_key"]}"')
    env_vars.append(f'APP_DEBUG={str(config["debug"]).lower()}')
    env_vars.append(f'APP_JWT_SECRET_KEY="{config["jwt_secret_key"]}"')
    env_vars.append(f'APP_JWT_ALGORITHM="{config["jwt_algorithm"]}"')
    env_vars.append(f'APP_JWT_EXPIRATION_HOURS={config["jwt_expiration_hours"]}')
    
    return "\n".join(env_vars)

def create_python_dict(config):
    """Create Python dictionary representation"""
    return f'''
# Python dictionary for AppSettings
app_settings_data = {{
    "secret_key": "{config["secret_key"]}",
    "debug": {config["debug"]},
    "jwt_secret_key": "{config["jwt_secret_key"]}",
    "jwt_algorithm": "{config["jwt_algorithm"]}",
    "jwt_expiration_hours": {config["jwt_expiration_hours"]}
}}
'''

def create_pydantic_example(config):
    """Create example of how to use with Pydantic"""
    return f'''
# Example: Creating AppSettings instance directly
from pydantic import SecretStr
from app.config import AppSettings

# Option 1: Using environment variables (recommended)
# Set the environment variables first, then:
app_settings = AppSettings()

# Option 2: Direct instantiation (for testing)
app_settings = AppSettings(
    secret_key=SecretStr("{config["secret_key"]}"),
    debug={config["debug"]},
    jwt_secret_key=SecretStr("{config["jwt_secret_key"]}"),
    jwt_algorithm="{config["jwt_algorithm"]}",
    jwt_expiration_hours={config["jwt_expiration_hours"]}
)

# Accessing the values
print("Secret key length:", len(app_settings.secret_key.get_secret_value()))
print("JWT algorithm:", app_settings.jwt_algorithm)
print("Token expires in:", app_settings.jwt_expiration_hours, "hours")
'''

def main():
    """Generate and display AppSettings configuration"""
    print("🔐 Generating AppSettings Configuration Data")
    print("=" * 50)
    
    # Generate configuration
    config = generate_app_settings_config()
    
    print("\n📋 Generated Configuration:")
    print("-" * 30)
    for key, value in config.items():
        if "secret" in key.lower():
            display_value = f"{str(value)[:15]}... (length: {len(str(value))})"
        else:
            display_value = value
        print(f"{key}: {display_value}")
    
    print("\n🌍 Environment Variables (.env file):")
    print("-" * 40)
    env_content = create_env_variables(config)
    print(env_content)
    
    # Save to .env file
    try:
        with open(".env", "a") as f:
            f.write("\n\n" + env_content + "\n")
        print("\n✅ Appended to .env file")
    except Exception as e:
        print(f"\n⚠️  Could not write to .env file: {e}")
    
    print("\n🐍 Python Dictionary:")
    print("-" * 20)
    print(create_python_dict(config))
    
    print("\n💻 Pydantic Usage Example:")
    print("-" * 25)
    print(create_pydantic_example(config))
    
    print("\n🔧 JWT Token Information:")
    print("-" * 25)
    print(f"Algorithm: {config['jwt_algorithm']}")
    print(f"Expiration: {config['jwt_expiration_hours']} hours")
    print(f"Secret length: {len(config['jwt_secret_key'])} characters")
    print("Security: Cryptographically secure random generation")
    
    print("\n📝 Next Steps:")
    print("1. Copy the environment variables to your .env file")
    print("2. Restart your application to load new config")
    print("3. Test with: python -c 'from app.config import app_config; print(app_config.jwt_algorithm)'")

if __name__ == "__main__":
    main()
