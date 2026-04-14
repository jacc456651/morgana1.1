from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Request
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging
import bcrypt
import jwt
import secrets
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ.get('JWT_SECRET', 'default-secret-change-me')
JWT_ALGORITHM = 'HS256'

app = FastAPI()
api_router = APIRouter(prefix="/api")

# ── Password helpers ──
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: str, email: str) -> str:
    payload = {
        'sub': user_id,
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24),
        'type': 'access'
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Not authenticated')
    token = auth_header[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get('type') != 'access':
            raise HTTPException(status_code=401, detail='Invalid token type')
        user = await db.users.find_one({'_id': ObjectId(payload['sub'])})
        if not user:
            raise HTTPException(status_code=401, detail='User not found')
        user['_id'] = str(user['_id'])
        user.pop('password_hash', None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')

async def get_optional_user(request: Request):
    try:
        return await get_current_user(request)
    except HTTPException:
        return None

# ── Models ──
  class StatusCheck(BaseModel):
      class Config:
          extra = 'ignore'
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class FavoriteCreate(BaseModel):
    caceria_id: str
    caceria_name: str

class UserRegister(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

# ── Auth endpoints ──
@api_router.post('/auth/register')
async def register(input: UserRegister):
    email = input.email.lower().strip()
    if not email or not input.password or len(input.password) < 6:
        raise HTTPException(status_code=400, detail='Email and password (min 6 chars) required')
    existing = await db.users.find_one({'email': email})
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    hashed = hash_password(input.password)
    user_doc = {
        'email': email,
        'password_hash': hashed,
        'name': input.name.strip(),
        'role': 'user',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    token = create_access_token(user_id, email)
    return {'user': {'id': user_id, 'email': email, 'name': input.name.strip(), 'role': 'user'}, 'token': token}

@api_router.post('/auth/login')
async def login(input: UserLogin):
    email = input.email.lower().strip()
    user = await db.users.find_one({'email': email})
    if not user or not verify_password(input.password, user['password_hash']):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    user_id = str(user['_id'])
    token = create_access_token(user_id, email)
    return {'user': {'id': user_id, 'email': email, 'name': user.get('name', ''), 'role': user.get('role', 'user')}, 'token': token}

@api_router.get('/auth/me')
async def me(request: Request):
    user = await get_current_user(request)
    return {'id': user['_id'], 'email': user['email'], 'name': user.get('name', ''), 'role': user.get('role', 'user')}

# ── Favorites (user-scoped when authenticated, anonymous otherwise) ──
@api_router.get('/favorites')
async def get_favorites(request: Request):
    user = await get_optional_user(request)
    if user:
        favs = await db.user_favorites.find({'user_id': user['_id']}, {'_id': 0}).to_list(100)
    else:
        favs = await db.favorites.find({}, {'_id': 0}).to_list(100)
    for f in favs:
        if isinstance(f.get('created_at'), str):
            f['created_at'] = f['created_at']
    return favs

@api_router.post('/favorites')
async def create_favorite(input: FavoriteCreate, request: Request):
    user = await get_optional_user(request)
    if user:
        existing = await db.user_favorites.find_one({'user_id': user['_id'], 'caceria_id': input.caceria_id}, {'_id': 0})
        if existing:
            return existing
        fav = {
            'id': str(uuid.uuid4()),
            'user_id': user['_id'],
            'caceria_id': input.caceria_id,
            'caceria_name': input.caceria_name,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.user_favorites.insert_one(fav)
        return {k: v for k, v in fav.items() if k != '_id'}
    else:
        existing = await db.favorites.find_one({'caceria_id': input.caceria_id}, {'_id': 0})
        if existing:
            return existing
        fav = {
            'id': str(uuid.uuid4()),
            'caceria_id': input.caceria_id,
            'caceria_name': input.caceria_name,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await db.favorites.insert_one(fav)
        return {k: v for k, v in fav.items() if k != '_id'}

@api_router.delete('/favorites/{caceria_id}')
async def delete_favorite(caceria_id: str, request: Request):
    user = await get_optional_user(request)
    if user:
        result = await db.user_favorites.delete_one({'user_id': user['_id'], 'caceria_id': caceria_id})
    else:
        result = await db.favorites.delete_one({'caceria_id': caceria_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Favorite not found')
    return {'message': 'Favorite removed', 'caceria_id': caceria_id}

# ── Status check ──
@api_router.get("/")
async def root():
    return {"message": "MORGANA Finviz Guide API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(**input.model_dump())
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for c in checks:
        if isinstance(c['timestamp'], str):
            c['timestamp'] = datetime.fromisoformat(c['timestamp'])
    return checks

# ── App setup ──
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup():
    await db.users.create_index('email', unique=True)
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@morgana.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'Morgana2026!')
    existing = await db.users.find_one({'email': admin_email})
    if not existing:
        hashed = hash_password(admin_password)
        await db.users.insert_one({
            'email': admin_email,
            'password_hash': hashed,
            'name': 'Admin MORGANA',
            'role': 'admin',
            'created_at': datetime.now(timezone.utc).isoformat()
        })
        logger.info(f'Admin user seeded: {admin_email}')
    elif not verify_password(admin_password, existing['password_hash']):
        await db.users.update_one({'email': admin_email}, {'$set': {'password_hash': hash_password(admin_password)}})
        logger.info('Admin password updated')

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
