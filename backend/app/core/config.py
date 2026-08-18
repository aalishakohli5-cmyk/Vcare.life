import os
import sys
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_SECRET_KEY")
    BLAND_AI_API_KEY: str = os.getenv("BLAND_AI_API_KEY")
    BLAND_WEBHOOK_SECRET: str = os.getenv("BLAND_WEBHOOK_SECRET", "dev-secret")
    
    def __init__(self):
        """Validate all required environment variables at startup"""
        missing_vars = []
        
        if not self.SUPABASE_URL:
            missing_vars.append("SUPABASE_URL")
        if not self.SUPABASE_KEY:
            missing_vars.append("SUPABASE_SECRET_KEY")
        if not self.BLAND_AI_API_KEY:
            missing_vars.append("BLAND_AI_API_KEY")
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            print(f"FATAL: {error_msg}")
            sys.exit(1)

settings = Settings()