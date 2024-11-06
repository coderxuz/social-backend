from fastapi import UploadFile, Depends, HTTPException, status, APIRouter, Request , File
from app.database import get_db
from sqlalchemy.orm import Session
from app.utils import save_image
from app.api.auth import oauth2_scheme
from app.models import Image
from app.schemas import ImageResponse
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