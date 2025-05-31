from typing import Optional
import hashlib
import uuid
from datetime import datetime
from db import db
from model.auth_model import UserResponse, SessionResponse

class AuthRepository:
    
    def _hash_password(self, password: str) -> str:
        """Simple password hashing using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    async def create_user(self, username: str, email: str, password: str) -> Optional[UserResponse]:
        """Create a new user"""
        password_hash = self._hash_password(password)
        
        query = """
            INSERT INTO "user" (username, email, password_hash, admin)
            VALUES ($1, $2, $3, false)
            RETURNING id_user, username, email, admin
        """
        
        try:
            async with db.get_connection() as conn:
                # Use a transaction to ensure atomicity
                async with conn.transaction():
                    row = await conn.fetchrow(query, username, email, password_hash)
                    if row:
                        # Convert UUID to string for Pydantic model
                        row_dict = dict(row)
                        row_dict['id_user'] = str(row_dict['id_user'])
                        return UserResponse(**row_dict)
                    return None
        except Exception as e:
            # Log the specific error for debugging
            print(f"Failed to create user: {e}")
            return None  # User already exists or other error
    
    async def verify_user(self, email: str, password: str) -> Optional[UserResponse]:
        """Verify user credentials and return user if valid"""
        password_hash = self._hash_password(password)
        
        query = """
            SELECT id_user, username, email, admin
            FROM "user"
            WHERE email = $1 AND password_hash = $2
        """
        
        async with db.get_connection() as conn:
            row = await conn.fetchrow(query, email, password_hash)
            if row:
                # Convert UUID to string for Pydantic model
                row_dict = dict(row)
                row_dict['id_user'] = str(row_dict['id_user'])
                return UserResponse(**row_dict)
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Check if user exists by email"""
        query = """
            SELECT id_user, username, email, admin
            FROM "user"
            WHERE email = $1
        """
        
        async with db.get_connection() as conn:
            row = await conn.fetchrow(query, email)
            if row:
                # Convert UUID to string for Pydantic model
                row_dict = dict(row)
                row_dict['id_user'] = str(row_dict['id_user'])
                return UserResponse(**row_dict)
            return None

    async def create_session(self, user_id: str, ip: str, device_details: str = None) -> Optional[SessionResponse]:
        """Create a new user session"""
        query = """
            INSERT INTO session (id_user, ip, device_details, logged_at)
            VALUES ($1, $2, $3, now())
            RETURNING id_session, id_user, ip, device_details, logged_at
        """
        
        async with db.get_connection() as conn:
            row = await conn.fetchrow(query, user_id, ip, device_details)
            if row:
                # Convert UUID to string for Pydantic model
                row_dict = dict(row)
                row_dict['id_user'] = str(row_dict['id_user'])
                return SessionResponse(**row_dict)
            return None
    
    async def get_session(self, session_id: int) -> Optional[SessionResponse]:
        """Get session by ID"""
        query = """
            SELECT id_session, id_user, ip, device_details, logged_at
            FROM session
            WHERE id_session = $1
        """
        
        async with db.get_connection() as conn:
            row = await conn.fetchrow(query, session_id)
            if row:
                # Convert UUID to string for Pydantic model
                row_dict = dict(row)
                row_dict['id_user'] = str(row_dict['id_user'])
                return SessionResponse(**row_dict)
            return None

# Global repository instance
auth_repo = AuthRepository()
