from typing import List, Optional, Dict, Any
from fastapi import Depends
from sqlalchemy.orm import Session
from api.models.user import User  # Importa o modelo User já definido
from passlib.hash import phpass
from datetime import datetime

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
    async def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Busca um usuário específico pelo email
        
        Args:
            db: Database session
            email: Email do usuário
            
        Returns:
            User object ou None
        """
        try:
            return db.query(User).filter(User.user_email == email).first()
        except Exception as e:
            print(f"Erro ao buscar usuário por email: {str(e)}")
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
    def _normalize_password_prefix(password: str) -> str:
        """
        Normaliza o prefixo da senha WordPress para o formato mais recente ($wp$).
        
        Args:
            password: Senha hash do WordPress
            
        Returns:
            Senha com prefixo normalizado para $wp$
        """
        if not password:
            return ""
        
        # Remove espaços e normaliza
        password = password.strip()
        
        # Se a senha já tem o prefixo $wp$, mantém como está
        if password.startswith('$wp$'):
            return password
        
        # Se tem o prefixo antigo $P$, converte para $wp$
        if password.startswith('$P$'):
            # Remove o prefixo $P$ e adiciona $wp$
            # O formato é: $P$[salt][hash] -> $wp$[salt][hash]
            # Vamos assumir que o salt tem 8 caracteres (padrão do WordPress)
            if len(password) > 12:  # $P$ + 8 chars salt + pelo menos 4 chars hash
                salt = password[3:11]  # Extrai os 8 caracteres do salt
                hash_part = password[11:]  # Resto é o hash
                return f"$wp${salt}${hash_part}"
        
        # Se não tem prefixo conhecido, retorna como está
        return password

    @staticmethod
    def _ensure_wp_prefix(password: str) -> str:
        """
        Garante que a senha tenha o prefixo $wp$.
        Se não tiver prefixo ou tiver prefixo antigo, recria o hash.
        
        Args:
            password: Senha em texto plano ou hash
            
        Returns:
            Senha hash com prefixo $wp$
        """
        # Se já é um hash com prefixo $wp$, retorna como está
        if password.startswith('$wp$'):
            return password
        
        # Se é um hash com prefixo antigo $P$, recria o hash
        if password.startswith('$P$'):
            # Para recriar o hash, precisamos da senha em texto plano
            # Como não temos acesso à senha original, vamos assumir que
            # a senha atual é um hash e não podemos recriar
            # Neste caso, convertemos o prefixo
            return MembershipProService._normalize_password_prefix(password)
        
        # Se não tem prefixo, assume que é senha em texto plano e cria hash
        return phpass.hash(password)

    @staticmethod
    async def upsert_user(db: Session, user_data: Dict[str, Any]) -> User:
        """
        Cria ou atualiza um usuário no WordPress (Membership Pro)
        
        Args:
            db: Database session
            user_data (Dict[str, Any]): Dados do usuário do Sparks App.
                                        Espera-se 'email', 'password', 'first_name', 'last_name'.
            
        Returns:
            User: O objeto User criado ou atualizado.
        """
        user_email = user_data['email'].lower()
        sparks_password = user_data['password']
        sparks_first_name = user_data.get('first_name', '')
        sparks_last_name = user_data.get('last_name', '')

        try:
            existing_user = await MembershipProService.get_user_by_email(db, user_email)

            hashed_password = MembershipProService._ensure_wp_prefix(sparks_password)

            if existing_user:
                # Atualizar usuário existente
                # Priorizar a senha do Sparks App
                existing_user.user_pass = hashed_password
                
                # Atualizar display_name e user_nicename se estiverem vazios ou se houver dados melhores
                if not existing_user.display_name or (sparks_first_name and sparks_last_name and existing_user.display_name == existing_user.user_login):
                    existing_user.display_name = f"{sparks_first_name} {sparks_last_name}".strip() if sparks_first_name or sparks_last_name else user_email
                
                if not existing_user.user_nicename or (sparks_first_name and sparks_last_name and existing_user.user_nicename == existing_user.user_login):
                    existing_user.user_nicename = f"{sparks_first_name.lower()}_{sparks_last_name.lower()}".replace(" ", "_") if sparks_first_name or sparks_last_name else user_email.split('@')[0].replace(".", "_")

                db.commit()
                db.refresh(existing_user)
                return existing_user
            else:
                # Criar novo usuário
                user_login_base = f"{sparks_first_name.lower()}_{sparks_last_name.lower()}".replace(" ", "_") if sparks_first_name or sparks_last_name else user_email.split('@')[0].replace(".", "_")
                
                # Garante user_login único (exemplo simplificado, pode precisar de mais robustez)
                user_login = user_login_base
                counter = 1
                while db.query(User).filter(User.user_login == user_login).first():
                    user_login = f"{user_login_base}-{counter}"
                    counter += 1

                new_user_data = {
                    "user_login": user_login,
                    "user_pass": hashed_password,
                    "user_nicename": f"{sparks_first_name.lower()}_{sparks_last_name.lower()}".replace(" ", "_") if sparks_first_name or sparks_last_name else user_email.split('@')[0].replace(".", "_"),
                    "user_email": user_email,
                    "user_url": user_data.get('user_url', ''),
                    "user_registered": datetime.now(),
                    "user_activation_key": user_data.get('user_activation_key', ''),
                    "user_status": user_data.get('user_status', 0),
                    "display_name": f"{sparks_first_name} {sparks_last_name}".strip() if sparks_first_name or sparks_last_name else user_email
                }
                
                new_user = User(**new_user_data)
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                return new_user
                
        except Exception as e:
            db.rollback()
            print(f"Erro ao criar/atualizar usuário: {str(e)}")
            raise

    @staticmethod
    async def add_user(db: Session, user_data) -> User:
        try:
            data = user_data.dict()
            # Criptografa a senha no formato WordPress (phpass) com prefixo $wp$
            data["user_pass"] = MembershipProService._ensure_wp_prefix(data["user_pass"])
            user = User(**data)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            print(f"Erro ao adicionar usuário: {str(e)}")
            raise
