from builtins import int
from fastapi import UploadFile, Depends, HTTPException, status, APIRouter, Request , File
from app.database import get_db
from sqlalchemy.orm import Session
from app.utils import save_image, get_user_from_token
from app.api.auth import oauth2_scheme
from app.models import Image
from app.schemas import ImageResponse, ImageUser
from pathlib import Path
from fastapi.responses import FileResponse

router = APIRouter(prefix='/image', tags=['IMAGE'])

@router.post('/', response_model=ImageResponse)
async def image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path=await save_image(file=file)
    new_image = Image(file_path = file_path)          
    db.add(new_image)
    db.commit()
    return {'image_id':new_image.id}
@router.get('/{id}')
async def image(id:int, db: Session = Depends(get_db)):
    image = db.query(Image).filter(Image.id == id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='image not found')
    image_path = Path(image.file_path)
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found on the server")
    return FileResponse(image_path)

@router.post('/user', response_model=ImageUser)
async def image(request:Request,file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_user = await get_user_from_token(request=request, database=db)
    print(db_user.username)
    file_path=await save_image(file=file)
    new_image = Image(file_path = file_path)          
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    db_user.user_img = new_image.id
    db.commit()
    user_image_url = f"{request.url.scheme}://{request.url.netloc}/image/{db_user.user_img}"
    return {'user_image': user_image_url}