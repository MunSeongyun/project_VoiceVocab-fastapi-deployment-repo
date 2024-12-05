from typing import Dict
from fastapi import APIRouter, Body, Depends, Path, Request, UploadFile , File
from services import auth_service

router = APIRouter(prefix='/test')


    