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
        'voice_file_url': voice_file_url,
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

@router.get('/csv/{vocabulary_id}')
async def csv(vocabulary_id:int = Path(title='단어장의 아이디', gt=0)):
    return await '하나의 단어장을 확인하기 위해, 유저가 id를 보내면, 권환 확인후 s3버킷에 있는 csv파일 전송'

@router.get('/script/{vocabulary_id}')
async def script(vocabulary_id:int = Path(title='단어장의 아이디', gt=0)):
    return await '단어장의 스크립트를 확인하기 위해 유저가 id를 보내면, 권한 확인 후 s3버킷에 있는 스크립트 파일 전송'

# body 사용함
@router.get('/known')
async def known():
    return await '유저가 단어장에서 이제 알겠다고 한 단어들은, 이미 알고있는 단어들 테이블에 추가하는 api'

@router.get('/knwon-list')
async def knwon_list():
    return await '유저에게 이미 알고있는 단어 전체를 보내주는 api'