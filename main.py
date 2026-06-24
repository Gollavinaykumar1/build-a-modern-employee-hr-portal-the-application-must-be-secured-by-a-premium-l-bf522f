# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from sqlalchemy import Column, String, Integer, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date
from typing import List
from jose import jwt
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI App
app = FastAPI()

# CORS Configuration
origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 Configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Password Context
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

# Define User Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

# Define Employee Model
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    department = Column(String)
    role = Column(String)
    employment_status = Column(String)

# Define Token Model
class Token(BaseModel):
    access_token: str
    token_type: str

# Define Token Data Model
class TokenData(BaseModel):
    username: str | None = None

# Define Employee Data Model
class EmployeeData(BaseModel):
    name: str
    department: str
    role: str
    employment_status: str

# Define Login Request Model
class LoginRequest(BaseModel):
    username: str
    password: str

# Verify Password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Get Password Hash
def get_password_hash(password):
    return pwd_context.hash(password)

# Authenticate User
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

# Create Access Token
def create_access_token(data: dict, expires_delta: int | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = date.today() + expires_delta
    else:
        expire = date.today() + 15
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "secret_key", algorithm="HS256")
    return encoded_jwt

# Get Current User
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Access token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError:
        raise HTTPException(
            status_code=401,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# Register User
@app.post("/register")
async def register_user(username: str, email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return JSONResponse(content={"error": "Username already exists"}, status_code=400)
    user = db.query(User).filter(User.email == email).first()
    if user:
        return JSONResponse(content={"error": "Email already exists"}, status_code=400)
    new_user = User(username=username, email=email, password=get_password_hash(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return JSONResponse(content={"message": "User created successfully"}, status_code=201)

# Login User
@app.post("/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = 15
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Get Total Employees
@app.get("/total_employees")
async def get_total_employees(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_employees = db.query(Employee).count()
    return JSONResponse(content={"total_employees": total_employees}, status_code=200)

# Get Open Roles
@app.get("/open_roles")
async def get_open_roles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    open_roles = db.query(Employee).filter(Employee.employment_status == "Open").count()
    return JSONResponse(content={"open_roles": open_roles}, status_code=200)

# Get Pending Leave Requests
@app.get("/pending_leave_requests")
async def get_pending_leave_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pending_leave_requests = db.query(Employee).filter(Employee.employment_status == "On Leave").count()
    return JSONResponse(content={"pending_leave_requests": pending_leave_requests}, status_code=200)

# Get Employee Directory
@app.get("/employee_directory")
async def get_employee_directory(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employees = db.query(Employee).all()
    employee_directory = []
    for employee in employees:
        employee_directory.append({
            "name": employee.name,
            "department": employee.department,
            "role": employee.role,
            "employment_status": employee.employment_status
        })
    return JSONResponse(content={"employee_directory": employee_directory}, status_code=200)

# Add Employee
@app.post("/add_employee")
async def add_employee(employee_data: EmployeeData, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_employee = Employee(name=employee_data.name, department=employee_data.department, role=employee_data.role, employment_status=employee_data.employment_status)
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return JSONResponse(content={"message": "Employee added successfully"}, status_code=201)