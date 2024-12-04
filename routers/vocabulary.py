from fastapi import APIRouter, Body, Path, UploadFile , File
from common import types
from services import vocabulary_service

router = APIRouter(prefix='/vocabulary')

@router.post('/generate')
async def generate(file: UploadFile = File(...)):
    
    voice_file_url, word_list, script = await vocabulary_service.japan(file, user_id=1)
    
    return {
        'message':'단어 목록을 생성했습니다.',
        'wordList': word_list,
        'voiceFileUrl': voice_file_url,
        'script': script
    }

@router.post('/save')
async def save(body: types.SaveBody):
    
    await vocabulary_service.save(body,'남가현')
    
    return {
        'message':'단어장을 저장했습니다.'
    }

@router.get('/list/{user_id}')
async def list(user_id:int = Path(title='유저의 아이디', gt=0)):
    return {
        'message':'단어장 목록을 불러왔습니다.',
        'data': await vocabulary_service.get_list(user_id)
    }

@router.put('/list/{list_id}')
async def update_list_name(list_id:int = Path(title='유저의 아이디', gt=0), body:types.UpdateListName = Body(title='변경하고 싶은 이름')):
    await vocabulary_service.update_list_name(list_id=list_id, name=body.name)
    return {
        'message':'단어장 이름을 변경했습니다.'
    }

@router.post('/known')
async def known(body:types.AppendKnownWord):
    await vocabulary_service.append_known(user_id=1, word=body.word)
    return {
        'message':'단어를 추가했습니다'
    }

@router.get('/known-list/{user_id}')
async def known_list(user_id:int = Path(title='유저의 아이디', gt=0)):
    return {
        'data': await vocabulary_service.known_list(user_id),
        'message': '단어 목록을 불러왔습니다.'
    }