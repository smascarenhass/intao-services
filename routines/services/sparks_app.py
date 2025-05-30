import logging
from datetime import datetime
from typing import List, Dict
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from api.models.user import User
from api.services.database import SessionLocal

logger = logging.getLogger(__name__)

class SparksAppService:
    def __init__(self):
        # Configuração do banco de dados do Sparks App
        self.sparks_db_url = "postgresql://tsdb:mkTaAhqyjUDp8W4LAgvZcLZsY2cFDa8c@49.12.213.74:5432/tshaped"
        self.sparks_engine = create_engine(self.sparks_db_url)
        self.sparks_session = Session(self.sparks_engine)
        
        # Configuração do banco de dados do Membership
        self.membership_db = SessionLocal()
        
    def __del__(self):
        self.sparks_session.close()
        self.membership_db.close()

    def alter_password_field_size(self) -> bool:
        """
        Altera o tamanho do campo password na tabela users para acomodar senhas mais longas
        
        Returns:
            bool: True se a alteração foi bem sucedida, False caso contrário
        """
        try:
            # Primeiro, verifica o tamanho atual do campo
            check_query = text("""
                SELECT character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'password'
            """)
            result = self.sparks_session.execute(check_query).scalar()
            
            if result and result < 255:
                # Altera o tamanho do campo para 255 caracteres
                alter_query = text("""
                    ALTER TABLE users 
                    ALTER COLUMN password TYPE varchar(255)
                """)
                self.sparks_session.execute(alter_query)
                self.sparks_session.commit()
                logger.info("Successfully altered password field size to 255 characters")
                return True
            else:
                logger.info("Password field is already large enough")
                return True
                
        except Exception as e:
            self.sparks_session.rollback()
            logger.error(f"Error altering password field size: {str(e)}")
            return False
        
    def get_sparks_users(self) -> List[Dict]:
        """
        Get all users from Sparks App database
        
        Returns:
            List[Dict]: List of users with their details
        """
        try:
            query = text("""
                SELECT id, email, password 
                FROM users 
                WHERE email IS NOT NULL
            """)
            result = self.sparks_session.execute(query)
            users = []
            for row in result:
                users.append({
                    'id': row[0],
                    'email': row[1].lower() if row[1] else None,  # Normaliza email para lowercase
                    'password': row[2]
                })
            logger.info(f"Successfully retrieved {len(users)} users from Sparks App database")
            return users
        except Exception as e:
            logger.error(f"Error fetching users from Sparks App database: {str(e)}", exc_info=True)
            raise

    def sync_passwords(self) -> Dict[str, int]:
        """
        Sync passwords from Membership Pro to Sparks App for matching users
        
        Returns:
            Dict[str, int]: Statistics about the sync operation
        """
        stats = {
            "total_membership_users": 0,
            "total_sparks_users": 0,
            "matching_users": 0,
            "updated_passwords": 0,
            "errors": 0
        }
        
        try:
            # Primeiro, altera o tamanho do campo password se necessário
            if not self.alter_password_field_size():
                raise Exception("Failed to alter password field size")
            
            # Get all users from both systems
            membership_users = self.membership_db.query(User).all()
            sparks_users = self.get_sparks_users()
            
            stats["total_membership_users"] = len(membership_users)
            stats["total_sparks_users"] = len(sparks_users)
            
            # Create a map of email to Sparks user for faster lookup
            sparks_user_map = {user["email"]: user for user in sparks_users if user["email"]}
            
            # For each membership user, try to update their Sparks password
            for membership_user in membership_users:
                email = membership_user.user_email.lower()
                if email in sparks_user_map:
                    stats["matching_users"] += 1
                    sparks_user = sparks_user_map[email]
                    
                    # Check if passwords are different
                    if sparks_user["password"] != membership_user.user_pass:
                        try:
                            # Update password in Sparks App database
                            query = text("""
                                UPDATE users 
                                SET password = :password 
                                WHERE email = :email
                            """)
                            self.sparks_session.execute(
                                query, 
                                {
                                    "password": membership_user.user_pass,
                                    "email": email
                                }
                            )
                            self.sparks_session.commit()
                            
                            stats["updated_passwords"] += 1
                            logger.info(f"Successfully synced password for user: {email}")
                        except Exception as e:
                            self.sparks_session.rollback()
                            stats["errors"] += 1
                            logger.error(f"Failed to sync password for user {email}: {str(e)}")
            
            return stats
                        
        except Exception as e:
            logger.error(f"Error during password sync: {str(e)}", exc_info=True)
            raise

# For backward compatibility
def get_sparks_app_users():
    service = SparksAppService()
    return service.get_sparks_users()
