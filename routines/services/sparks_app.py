import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from api.models.user import User
from api.services.database import SessionLocal
import os

logger = logging.getLogger(__name__)

class SparksAppService:
    def __init__(self):
        self.api_url = "https://internal.intao.app/api/cockpit/sparks-app/users"
        
        # Configuração do banco de dados do Membership
        self.membership_db = SessionLocal()
        
        # Configuração do banco de dados do Sparks App (PostgreSQL)
        sparks_db_url = "postgresql://tsdb:mkTaAhqyjUDp8W4LAgvZcLZsY2cFDa8c@database.intao.app:5432/tshaped"
        self.sparks_engine = create_engine(sparks_db_url, echo=False)  # Disable SQL query logging
        self.sparks_session = Session(self.sparks_engine)
        
        # Garante que a coluna last_password_sync existe
        self._ensure_sync_column_exists()
        
    def _ensure_sync_column_exists(self):
        """
        Garante que a coluna last_password_sync existe na tabela users.
        Se não existir, cria a coluna.
        """
        try:
            # Verifica se a coluna existe
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'last_password_sync'
            """)
            
            result = self.sparks_session.execute(check_query).fetchone()
            
            if not result:
                # Se a coluna não existe, cria ela
                create_query = text("""
                    ALTER TABLE users 
                    ADD COLUMN last_password_sync TIMESTAMP
                """)
                self.sparks_session.execute(create_query)
                self.sparks_session.commit()
                logger.info("Coluna last_password_sync criada com sucesso")
            else:
                logger.info("Coluna last_password_sync já existe")
                
        except Exception as e:
            logger.error(f"Erro ao verificar/criar coluna last_password_sync: {str(e)}")
            raise

    def _normalize_password_prefix(self, password: str) -> str:
        """
        Normaliza o prefixo da senha WordPress para comparação.
        Converte prefixos antigos ($P$) para o formato mais recente ($wp$).
        
        Args:
            password: Senha hash do WordPress
            
        Returns:
            Senha com prefixo normalizado
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

    def _normalize_password(self, password: str) -> str:
        """
        Normaliza a senha para comparação, removendo espaços em branco,
        truncando para o tamanho máximo do banco de dados e normalizando prefixos.
        """
        if not password:
            return ""
        
        # Primeiro normaliza o prefixo
        normalized = self._normalize_password_prefix(password)
        
        # Depois trunca para o tamanho máximo
        return normalized[:60]

    def _passwords_match(self, membership_pass: str, sparks_pass: str) -> bool:
        """
        Compara as senhas de forma normalizada, considerando diferentes prefixos WordPress.
        """
        normalized_membership = self._normalize_password(membership_pass)
        normalized_sparks = self._normalize_password(sparks_pass)
        
        # Log para debug
        logger.debug(f"Comparando senhas:")
        logger.debug(f"Membership (original): {membership_pass[:15]}...")
        logger.debug(f"Sparks (original): {sparks_pass[:15]}...")
        logger.debug(f"Membership (normalizada): {normalized_membership[:15]}...")
        logger.debug(f"Sparks (normalizada): {normalized_sparks[:15]}...")
        
        return normalized_membership == normalized_sparks
        
    def __del__(self):
        if hasattr(self, 'sparks_session'):
            self.sparks_session.close()
        if hasattr(self, 'membership_db'):
            self.membership_db.close()

    def get_sparks_users(self) -> List[Dict]:
        """
        Get all users from Sparks App database
        
        Returns:
            List[Dict]: List of users with their details
        """
        try:
            logger.info("Executing query to get all users from Sparks App database...")
            query = text("""
                SELECT id, email, password, first_name, last_name, last_password_sync
                FROM users
                WHERE email IS NOT NULL
            """)
            print("\n=== QUERY EXECUTADA ===")
            print(query.text)
            print("======================\n")

            result = self.sparks_session.execute(query)
            users = []
            for row in result:
                users.append({
                    'id': row[0],
                    'email': row[1].lower() if row[1] else None,  # Normaliza email para lowercase
                    'password': row[2],
                    'first_name': row[3],
                    'last_name': row[4],
                    'last_password_sync': row[5]
                })
            logger.info(f"Successfully retrieved {len(users)} users from Sparks App database")
            return users
        except Exception as e:
            logger.error(f"Error fetching users from Sparks App database: {str(e)}", exc_info=True)
            raise

    def sync_passwords(self, membership_users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synchronizes passwords from Membership Pro to Sparks App.
        Makes sure users that exist in both systems have the same password as in Membership Pro.
        """
        try:
            # Get all users from Sparks App database
            print("\n=== QUERY EXECUTADA ===\n")
            query = text("""
                SELECT id, email, password, last_password_sync
                FROM users 
                WHERE email IS NOT NULL
            """)
            print(query)
            print("\n======================\n")
            
            sparks_users = self.sparks_session.execute(query).fetchall()
            print(f"Successfully retrieved {len(sparks_users)} users from Sparks App database")
            
            # Track synchronization statistics
            stats = {
                'total_membership_users': len(membership_users),
                'total_sparks_users': len(sparks_users),
                'matching_users': 0,
                'updated_passwords': 0,
                'skipped_syncs': 0,
                'errors': 0
            }
            
            # Process each membership user
            for membership_user in membership_users:
                membership_email = membership_user['email'].lower()
                membership_pass = membership_user['password']
                
                # Find matching Sparks user
                sparks_user = next((user for user in sparks_users if user.email.lower() == membership_email), None)
                
                if sparks_user:
                    stats['matching_users'] += 1
                    
                    print("\n" + "="*50)
                    print(f"VERIFICANDO USUÁRIO: {membership_email}")
                    print("="*50 + "\n")
                    
                    print(f"Senha do Membership: {membership_pass[:10]}...")
                    print(f"Senha atual no banco: {sparks_user.password[:10]}...")
                    
                    # Verifica se a senha já foi sincronizada recentemente (últimas 24 horas)
                    last_sync = sparks_user.last_password_sync
                    if last_sync and (datetime.now() - last_sync).total_seconds() < 86400:  # 24 horas em segundos
                        print("⏭️ SENHA SINCRONIZADA RECENTEMENTE - PULANDO ATUALIZAÇÃO")
                        stats['skipped_syncs'] += 1
                        continue
                    
                    # If passwords are different, update Sparks password
                    if not self._passwords_match(membership_pass, sparks_user.password):
                        print("\n🔄 SENHAS DIFERENTES - INICIANDO ATUALIZAÇÃO")
                        try:
                            # Truncate password to 60 characters to match database field size
                            truncated_password = self._normalize_password(membership_pass)
                            
                            # Update password in Sparks App database
                            update_query = text("""
                                UPDATE users 
                                SET password = :password,
                                    last_password_sync = :sync_time
                                WHERE email = :email
                                RETURNING id, email, password, last_password_sync
                            """)
                            
                            result = self.sparks_session.execute(
                                update_query, 
                                {
                                    "password": truncated_password,
                                    "email": membership_email,
                                    "sync_time": datetime.now()
                                }
                            )
                            
                            # Verify the update
                            updated_user = result.fetchone()
                            if updated_user and self._passwords_match(truncated_password, updated_user.password):
                                stats['updated_passwords'] += 1
                                print(f"✅ Senha atualizada com sucesso para {membership_email}")
                            else:
                                stats['errors'] += 1
                                print(f"❌ Erro ao verificar atualização para {membership_email}")
                                
                        except Exception as e:
                            stats['errors'] += 1
                            print(f"❌ Erro ao atualizar senha para {membership_email}: {str(e)}")
                    else:
                        print("✅ SENHAS IDÊNTICAS - PULANDO ATUALIZAÇÃO")
                    
                    print("="*50 + "\n")
            
            return stats
            
        except Exception as e:
            print(f"Error during password synchronization: {str(e)}")
            raise

# For backward compatibility
def get_sparks_app_users():
    service = SparksAppService()
    return service.get_sparks_users()
