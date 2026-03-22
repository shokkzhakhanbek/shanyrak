from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Shanyrak, Comment
from app.schemas import (
    ShanyrakCreate,
    ShanyrakUpdate,
    ShanyrakResponse,
    ShanyrakCreateResponse,
)
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/shanyraks", tags=["shanyraks"])


# Таск 5: Создание объявления
@router.post("/", response_model=ShanyrakCreateResponse)
def create_shanyrak(
    data: ShanyrakCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    shanyrak = Shanyrak(**data.model_dump(), user_id=current_user.id)
    db.add(shanyrak)
    db.commit()
    db.refresh(shanyrak)
    return ShanyrakCreateResponse(id=shanyrak.id)


# Таск 6 + 13: Получение объявления (с total_comments)
@router.get("/{id}", response_model=ShanyrakResponse)
def get_shanyrak(id: int, db: Session = Depends(get_db)):
    shanyrak = db.query(Shanyrak).filter(Shanyrak.id == id).first()
    if not shanyrak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shanyrak not found",
        )
    total_comments = (
        db.query(func.count(Comment.id))
        .filter(Comment.shanyrak_id == id)
        .scalar()
    )
    response = ShanyrakResponse.model_validate(shanyrak)
    response.total_comments = total_comments
    return response


# Таск 7: Изменение объявления
@router.patch("/{id}")
def update_shanyrak(
    id: int,
    data: ShanyrakUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    shanyrak = db.query(Shanyrak).filter(Shanyrak.id == id).first()
    if not shanyrak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shanyrak not found",
        )
    if shanyrak.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own shanyraks",
        )
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(shanyrak, key, value)
    db.commit()
    return {"message": "Shanyrak updated successfully"}


# Таск 8: Удаление объявления
@router.delete("/{id}")
def delete_shanyrak(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    shanyrak = db.query(Shanyrak).filter(Shanyrak.id == id).first()
    if not shanyrak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shanyrak not found",
        )
    if shanyrak.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own shanyraks",
        )
    db.delete(shanyrak)
    db.commit()
    return {"message": "Shanyrak deleted successfully"}