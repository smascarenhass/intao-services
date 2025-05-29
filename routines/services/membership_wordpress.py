import time
from datetime import datetime
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from api.models.user import User

logger = logging.getLogger(__name__)

class MembershipWordpressService:
    def __init__(self):
        # Configuração do banco de dados
        self.DB_USER = os.getenv("DB_USER", "unfbrbzgfgscg")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "meut1tbd0twk")
        self.DB_HOST = os.getenv("DB_HOST", "gfram1000.siteground.biz")
        self.DB_NAME = os.getenv("DB_NAME", "dblbufwzxkgog9")

        self.DATABASE_URL = f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}"
        
        # Criar engine e sessão
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    async def list_users(self, db):
        """Lista todos os usuários do Membership Pro"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{current_time}] Buscando usuários do Membership Pro...")
        
        try:
            # Buscar todos os usuários
            users = db.query(User).order_by(User.ID.desc()).all()
            
            # Exibir informações dos usuários
            logger.info(f"Total de usuários encontrados: {len(users)}")
            for user in users:
                logger.info(f"""
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