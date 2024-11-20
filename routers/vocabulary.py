from fastapi import APIRouter, Path

router = APIRouter(prefix='/vocabulary')

@router.get('/generate')
async def generate():
    return '''
    프론트에서 녹음파일 업로드 → 
    백엔드에서는 문자로 변환 및 단어 추출 후 
    해당 스크립트는 S3버킷에 저장하고, 
    이미 알고있는 단어 테이블에 없는 단어만 
    추출 후 프론트에게 스크립트 이름과 함께 전달
    '''

@router.get('/save')
async def save():
    return await '''
    받은 단어 목록 중 사용자가 선택하는 단어는 
    known_word_list, 아닌 단어는 word_list로 
    백엔드로 스크립트와 함께 전달 → 
    백엔드에서는 known_word_list는 
    이미아는단어테이블에 저장, word_list는 
    해당 단어들을 번역해서 CSV 파일로 제작 후 
    S3버킷에 업로드 후, 받은 스크립트 명과, 
    단어장의 파일 명과 유저 명을 사용해서 
    vocabulary_list 객체를 생성
'''

@router.get('/list/{user_id}')
async def list(user_id:int = Path(title='유저의 아이디', gt=0)):
    return await '유저가 단어장 목록을 확인하기 위해, 전체 vacabulary_list를 반환하는 api 필요'

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