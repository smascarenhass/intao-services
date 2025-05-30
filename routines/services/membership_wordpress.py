import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from api.models.user import User
from api.services.database import SessionLocal

logger = logging.getLogger(__name__)

class MembershipWordpressService:
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        self.db.close()

    async def list_users(self) -> List[User]:
        """
        Lista todos os usuários do WordPress
        
        Returns:
            List[User]: Lista de usuários encontrados
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{current_time}] Buscando usuários do WordPress...")
        
        try:
            users = self.db.query(User).order_by(User.ID.desc()).all()
            logger.info(f"Total de usuários encontrados: {len(users)}")
            
            for user in users:
                logger.debug(f"""
                ID: {user.ID}
                Nome: {user.display_name}
                Email: {user.user_email}
                Data de Registro: {user.user_registered}
                Status: {user.user_status}
                ------------------------
                """)
            
            return users
                
        except Exception as e:
            logger.error(f"Erro ao buscar usuários: {str(e)}")
            raise

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Busca um usuário específico pelo ID
        
        Args:
            user_id (int): ID do usuário
            
        Returns:
            Optional[User]: Usuário encontrado ou None
        """
        try:
            user = self.db.query(User).filter(User.ID == user_id).first()
            if user:
                logger.info(f"Usuário encontrado: {user.display_name} (ID: {user.ID})")
            else:
                logger.warning(f"Usuário não encontrado com ID: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Erro ao buscar usuário {user_id}: {str(e)}")
            raise

    async def update_user_status(self, user_id: int, status: int) -> bool:
        """
        Atualiza o status de um usuário
        
        Args:
            user_id (int): ID do usuário
            status (int): Novo status
            
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
                
            user.user_status = status
            self.db.commit()
            logger.info(f"Status do usuário {user_id} atualizado para {status}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao atualizar status do usuário {user_id}: {str(e)}")
            return False

    async def get_active_users(self) -> List[User]:
        """
        Retorna apenas usuários ativos (status = 0)
        
        Returns:
            List[User]: Lista de usuários ativos
        """
        try:
            users = self.db.query(User).filter(User.user_status == 0).all()
            logger.info(f"Total de usuários ativos: {len(users)}")
            return users
        except Exception as e:
            logger.error(f"Erro ao buscar usuários ativos: {str(e)}")
            raise