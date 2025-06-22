from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, EmailStr
from datetime import datetime
from ..services.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from routines.services.sparks_app import SparksAppService
import json

router = APIRouter(
    prefix="/api/sparks-app",
    tags=["sparks-app"]
)

class SparksUserResponse(BaseModel):
    id: int
    email: str
    password: str
    last_password_sync: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    name: Optional[str] = None
    role: Optional[Union[str, int]] = None
    status: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class SparksUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    name: Optional[str] = None
    role: Optional[Union[str, int]] = None
    status: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

@router.get("/users", response_model=List[SparksUserResponse])
async def get_sparks_users(
    db: Session = Depends(get_db)
):
    """
    Retorna todos os usuários do Sparks App com todos os campos
    """
    try:
        service = SparksAppService()
        query = text("""
            SELECT *
            FROM users 
            WHERE email IS NOT NULL
        """)
        result = service.sparks_session.execute(query)
        users = []
        for row in result:
            user_dict = dict(row._mapping)
            # Converte campos JSON se existirem
            if 'settings' in user_dict and user_dict['settings']:
                try:
                    user_dict['settings'] = json.loads(user_dict['settings'])
                except:
                    user_dict['settings'] = None
            users.append(user_dict)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuários: {str(e)}")

@router.get("/users/{user_id}", response_model=SparksUserResponse)
async def get_sparks_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Retorna detalhes de um usuário específico do Sparks App com todos os campos
    """
    try:
        service = SparksAppService()
        query = text("""
            SELECT *
            FROM users 
            WHERE id = :user_id
        """)
        result = service.sparks_session.execute(query, {"user_id": user_id})
        user = result.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
        user_dict = dict(user._mapping)
        # Converte campos JSON se existirem
        if 'settings' in user_dict and user_dict['settings']:
            try:
                user_dict['settings'] = json.loads(user_dict['settings'])
            except:
                user_dict['settings'] = None
                
        return user_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuário: {str(e)}")

@router.put("/users/{user_id}")
async def update_sparks_user(
    user_id: int,
    user_update: SparksUserUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza um usuário do Sparks App
    """
    try:
        service = SparksAppService()
        query = text("""
            SELECT *
            FROM users 
            WHERE id = :user_id
        """)
        result = service.sparks_session.execute(query, {"user_id": user_id})
        user = result.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
        # Atualiza os campos fornecidos
        update_data = {}
        for field, value in user_update.dict(exclude_unset=True).items():
            if value is not None:
                if field == 'settings' and isinstance(value, dict):
                    update_data[field] = json.dumps(value)
                else:
                    update_data[field] = value
            
        if not update_data:
            return {"message": "Nenhum campo para atualizar"}
            
        # Executa a atualização no banco de dados
        query = text("""
            UPDATE users 
            SET {fields}
            WHERE id = :user_id
            RETURNING *
        """.format(
            fields=", ".join([f"{k} = :{k}" for k in update_data.keys()])
        ))
        
        result = service.sparks_session.execute(
            query,
            {**update_data, "user_id": user_id}
        )
        service.sparks_session.commit()
        
        updated_user = result.fetchone()
        if not updated_user:
            raise HTTPException(status_code=500, detail="Erro ao atualizar usuário")
            
        user_dict = dict(updated_user._mapping)
        # Converte campos JSON se existirem
        if 'settings' in user_dict and user_dict['settings']:
            try:
                user_dict['settings'] = json.loads(user_dict['settings'])
            except:
                user_dict['settings'] = None
                
        return {
            "message": "Usuário atualizado com sucesso",
            "user": user_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_sparks_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove um usuário do Sparks App
    """
    try:
        service = SparksAppService()
        query = text("""
            SELECT *
            FROM users 
            WHERE id = :user_id
        """)
        result = service.sparks_session.execute(query, {"user_id": user_id})
        user = result.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
            
        # Remove o usuário do banco de dados
        query = text("""
            DELETE FROM users 
            WHERE id = :user_id
            RETURNING *
        """)
        
        result = service.sparks_session.execute(
            query,
            {"user_id": user_id}
        )
        service.sparks_session.commit()
        
        deleted_user = result.fetchone()
        if not deleted_user:
            raise HTTPException(status_code=500, detail="Erro ao remover usuário")
            
        user_dict = dict(deleted_user._mapping)
        # Converte campos JSON se existirem
        if 'settings' in user_dict and user_dict['settings']:
            try:
                user_dict['settings'] = json.loads(user_dict['settings'])
            except:
                user_dict['settings'] = None
                
        return {
            "message": "Usuário removido com sucesso",
            "user": user_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover usuário: {str(e)}") 