from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session
from api.models.user import User  # Importa o modelo User já definido
from passlib.hash import phpass

class MembershipProService:
    @staticmethod
    async def list_users(db: Session) -> List[User]:
        """
        Lists all users with all columns from xwh_users table
        
        Args:
            db: Database session
            
        Returns:
            List of users with all columns
        """
        try:
            # Using select * to get all columns
            return db.query(User).order_by(User.ID.desc()).all()
        except Exception as e:
            print(f"Erro ao listar usuários: {str(e)}")
            raise

    @staticmethod
    async def get_user_by_id(db: Session, user_id: int) -> User:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User object
        """
        try:
            return db.query(User).filter(User.ID == user_id).first()
        except Exception as e:
            print(f"Erro ao buscar usuário: {str(e)}")
            raise

    @staticmethod
    async def update_user_status(db: Session, user_id: int, status: str) -> bool:
        """
        Update user membership status
        
        Args:
            db: Database session
            user_id: User ID
            status: New status
            
        Returns:
            True if successful
        """
        try:
            user = db.query(User).filter(User.ID == user_id).first()
            if not user:
                return False
                
            # Aqui você pode adicionar a lógica para atualizar o status
            # Por exemplo, atualizar uma tabela de memberships
            
            return True
        except Exception as e:
            print(f"Erro ao atualizar status: {str(e)}")
            return False

    @staticmethod
    async def add_user(db: Session, user_data) -> User:
        try:
            data = user_data.dict()
            # Criptografa a senha no formato WordPress (phpass)
            data["user_pass"] = phpass.hash(data["user_pass"])
            user = User(**data)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            print(f"Erro ao adicionar usuário: {str(e)}")
            raise
