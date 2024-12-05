from typing import Dict
from fastapi import APIRouter, Body, Depends, Path, UploadFile , File
from common import types
from services import vocabulary_service, auth_service

router = APIRouter(prefix='/vocabulary')

@router.post('/generate')
async def generate(file: UploadFile = File(...),current_user : Dict = Depends(auth_service.get_current_user)):
    
    voice_file_url, word_list, script = await vocabulary_service.japan(file, user_id=int(current_user['sub']))
    
    return {
        'message':'단어 목록을 생성했습니다.',
        'wordList': word_list,
        'voiceFileUrl': voice_file_url,
        'script': script
    }

@router.post('/save')
async def save(body: types.SaveBody, current_user : Dict = Depends(auth_service.get_current_user)):
    
    await vocabulary_service.save(body,current_user['name'],int(current_user['sub']))
    
    return {
        'message':'단어장을 저장했습니다.'
    }

@router.get('/list')
async def list(current_user : Dict = Depends(auth_service.get_current_user)):
    return {
        'message':'단어장 목록을 불러왔습니다.',
        'data': await vocabulary_service.get_list(int(current_user['sub']))
    }

@router.put('/list/{list_id}')
async def update_list_name(list_id:int = Path(title='단어장의 아이디', gt=0), body:types.UpdateListName = Body(title='변경하고 싶은 이름'),current_user : Dict = Depends(auth_service.get_current_user)):
    await vocabulary_service.update_list_name(list_id=list_id, name=body.name, user_id=int(current_user['sub']))
    return {
        'message':'단어장 이름을 변경했습니다.'
    }

@router.post('/known')
async def known(body:types.AppendKnownWord,current_user : Dict = Depends(auth_service.get_current_user)):
    await vocabulary_service.append_known(user_id=int(current_user['sub']), word=body.word)
    return {
        'message':'단어를 추가했습니다'
    }

@router.get('/known-list')
async def known_list(current_user : Dict = Depends(auth_service.get_current_user)):
    return {
        'data': await vocabulary_service.known_list(int(current_user['sub'])),
        'message': '단어 목록을 불러왔습니다.'
    }