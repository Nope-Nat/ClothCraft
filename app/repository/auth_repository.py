from typing import Optional
import hashlib
import uuid
from datetime import datetime, timedelta
from db import db
from model.auth_model import UserResponse, SessionResponse, UserSessionData

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
    
    async def get_user_from_session(self, session_id: int) -> Optional[UserSessionData]:
        """Get user data from session ID"""
        query = """
            SELECT 
                u.id_user,
                u.username,
                u.email,
                u.admin as is_admin,
                s.id_session as session_id,
                s.logged_at,
                s.ip,
                s.device_details
            FROM session s
            JOIN "user" u ON s.id_user = u.id_user
            WHERE s.id_session = $1
        """
        
        async with db.get_connection() as conn:
            row = await conn.fetchrow(query, session_id)
            if row:
                # Convert UUID to string for Pydantic model
                row_dict = dict(row)
                row_dict['user_id'] = str(row_dict['id_user'])
                del row_dict['id_user']  # Remove the UUID version
                return UserSessionData(**row_dict)
            return None
    
    async def delete_session(self, session_id: int) -> bool:
        """Delete a session by ID"""
        query = "DELETE FROM session WHERE id_session = $1"
        
        async with db.get_connection() as conn:
            result = await conn.execute(query, session_id)
            return result == "DELETE 1"
    
    async def delete_old_sessions(self, older_than: datetime) -> int:
        """
        Delete sessions older than the specified timestamp
        
        Args:
            older_than: Delete sessions logged in before this timestamp
        
        Returns:
            Number of sessions deleted
        
        Example:
            # Delete sessions older than 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            deleted_count = await auth_repo.delete_old_sessions(cutoff_date)
        """
        query = "DELETE FROM session WHERE logged_at < $1"
        
        async with db.get_connection() as conn:
            result = await conn.execute(query, older_than)
            # Extract the number from "DELETE n" response
            return int(result.split()[-1]) if result.startswith("DELETE") else 0

# Global repository instance
auth_repo = AuthRepository()
