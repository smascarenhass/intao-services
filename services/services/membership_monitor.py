import time
from datetime import datetime
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from api.models.user import User  # Importando o modelo User

logger = logging.getLogger(__name__)

# Configuração do banco de dados
DB_USER = os.getenv("DB_USER", "unfbrbzgfgscg")
DB_PASSWORD = os.getenv("DB_PASSWORD", "meut1tbd0twk")
DB_HOST = os.getenv("DB_HOST", "gfram1000.siteground.biz")
DB_NAME = os.getenv("DB_NAME", "dblbufwzxkgog9")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Criar engine e sessão
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def monitor_membership_users():
    """Serviço que monitora e exibe os usuários do Membership Pro"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{current_time}] Verificando usuários do Membership Pro...")
    
    try:
        # Criar sessão do banco de dados
        db = SessionLocal()
        
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
            
    except Exception as e:
        logger.error(f"Erro ao monitorar usuários: {str(e)}")
    finally:
        db.close()
    
    logger.info(f"[{current_time}] Monitoramento de usuários concluído!") 