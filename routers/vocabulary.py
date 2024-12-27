from typing import Dict
from fastapi import APIRouter, Body, Depends, Path, UploadFile , File, Query, status
from common import types
from common import data_for_swagger
from services import vocabulary_service, auth_service

router = APIRouter(prefix='/vocabulary', tags=["vocabulary"])
                   

@router.post('/generate', status_code=status.HTTP_201_CREATED, summary="wav파일을 텍스트로 변경후 단어목록 생성", response_model=data_for_swagger.PostVocabulary)
async def generate(language:str = Query(default=None),file: UploadFile = File(...),current_user : Dict = Depends(auth_service.get_current_user)):
    
    voice_file_url, word_list, script = await vocabulary_service.generate_wav(file, user_id=int(current_user['sub']), language=language)
    
    return {
        'message':'단어 목록을 생성했습니다.',
        'wordList': word_list,
        'voiceFileUrl': voice_file_url,
        'language':language,
        'script': script
    }

@router.post('/generate_to_text', status_code=status.HTTP_201_CREATED, summary="텍스트에서 단어목록을 생성", response_model=data_for_swagger.PostGenerateToText)
async def generate_to_text(body : types.GenerateBody ,language:str = Query(default=None), current_user : Dict = Depends(auth_service.get_current_user)):
    word_list = await vocabulary_service.generate_text(body.text, user_id=int(current_user['sub']), language=language)
    return {
        'message':'단어 목록을 생성했습니다.',
        'wordList': word_list,
        'language':language,
        'script': body.text
    }
    
@router.post('/save',status_code=status.HTTP_201_CREATED, summary="단어장 생성", response_model=data_for_swagger.MessageOnly)
async def save(body: types.SaveBody, current_user : Dict = Depends(auth_service.get_current_user)):
    
    await vocabulary_service.save(body,current_user['name'],int(current_user['sub']))
    
    return {
        'message':'단어장을 저장했습니다.'
    }

@router.get('/list', status_code=status.HTTP_200_OK, summary="유저의 모든 단어장 불러오기", response_model=data_for_swagger.GetList)
async def list(current_user : Dict = Depends(auth_service.get_current_user)):
    list_all = await vocabulary_service.get_list(int(current_user['sub']))
    
    return {
        'message':'단어장 목록을 불러왔습니다.',
        'data': list_all
    }

@router.put('/list/{list_id}', status_code=status.HTTP_200_OK, summary="단어장 이름 변경", response_model=data_for_swagger.MessageOnly)
async def update_list_name(list_id:int = Path(title='단어장의 아이디', gt=0), body:types.UpdateListName = Body(title='변경하고 싶은 이름'),current_user : Dict = Depends(auth_service.get_current_user)):
    await vocabulary_service.update_list_name(list_id=list_id, name=body.name, user_id=int(current_user['sub']))
    return {
        'message':'단어장 이름을 변경했습니다.'
    }

@router.post('/known', status_code=status.HTTP_201_CREATED, summary="알고있는 단어 목록에 새로운 단어 추가", response_model=data_for_swagger.MessageOnly)
async def known(body:types.AppendKnownWord,current_user : Dict = Depends(auth_service.get_current_user)):
    await vocabulary_service.append_known(user_id=int(current_user['sub']), word=body.word)
    vocabulary_service.update_csv(user_id=int(current_user['sub']), content=body.content, vocabulary_id=body.vocabulary_id)
    return {
        'message':'단어를 추가했습니다'
    }

@router.get('/known-list',status_code=status.HTTP_200_OK, summary="알고있는 단어 목록 불러오기", response_model=data_for_swagger.GetKnownList)
async def known_list(current_user : Dict = Depends(auth_service.get_current_user)):
    return {
        'data': await vocabulary_service.known_list(int(current_user['sub'])),
        'message': '단어 목록을 불러왔습니다.'
    }

@router.get('/{target}/{vocabulary_id}',status_code=status.HTTP_200_OK, summary="단어장이나 스크립트를 가져옴", response_model=data_for_swagger.GetTarget)
async def get_file(target:str = Path(title='script or voca'),vocabulary_id:int = Path(title='단어장의 아이디', gt=0), current_user : Dict = Depends(auth_service.get_current_user)):
    data = await vocabulary_service.get_voca_or_script(vocabulary_id, int(current_user['sub']), target)
    return {
        'message':'단어장을 가져왔습니다.',
        'data':data
    }