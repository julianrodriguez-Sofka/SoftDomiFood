from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from services.auth_service import verify_password, get_password_hash, create_access_token, decode_token
from services.database_service import get_user_by_email, create_user

router = APIRouter()
security = HTTPBearer()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtener usuario actual desde token"""
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

@router.post("/register")
async def register(request: RegisterRequest):
    """Registro de usuario"""
    # Verificar si el usuario ya existe
    existing_user = await get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash de contraseña
    hashed_password = get_password_hash(request.password)
    
    # Crear usuario
    user = await create_user(request.email, hashed_password, request.name, request.phone)
    if not user:
        raise HTTPException(status_code=500, detail="Error creating user")
    
    # Generar token
    token = create_access_token({"userId": user["id"], "role": user["role"]})
    
    return {
        "message": "User created successfully",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "phone": user.get("phone"),
            "role": user["role"]
        },
        "token": token
    }

@router.post("/login")
async def login(request: LoginRequest):
    """Login de usuario"""
    # Buscar usuario
    user = await get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verificar contraseña
    if not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generar token
    token = create_access_token({"userId": user["id"], "role": user["role"]})
    
    return {
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "phone": user.get("phone"),
            "role": user["role"]
        },
        "token": token
    }

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Obtener perfil del usuario actual"""
    # Obtener información completa del usuario desde la base de datos
    from services.database_service import get_user_by_id
    user_id = current_user.get("userId")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuario no autenticado")
    
    # Buscar usuario por ID
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "id": user.get("id"),
        "userId": user.get("id"),
        "role": user.get("role"),
        "email": user.get("email", ""),
        "name": user.get("name", ""),
        "phone": user.get("phone")
    }

