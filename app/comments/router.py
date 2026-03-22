from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Shanyrak, Comment
from app.schemas import (
    CommentCreate,
    CommentUpdate,
    CommentsListResponse,
)
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/shanyraks/{shanyrak_id}/comments", tags=["comments"])


def _get_shanyrak_or_404(shanyrak_id: int, db: Session) -> Shanyrak:
    shanyrak = db.query(Shanyrak).filter(Shanyrak.id == shanyrak_id).first()
    if not shanyrak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shanyrak not found",
        )
    return shanyrak


def _get_comment_or_404(comment_id: int, shanyrak_id: int, db: Session) -> Comment:
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.shanyrak_id == shanyrak_id)
        .first()
    )
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    return comment


# Таск 9: Добавление комментария
@router.post("/")
def create_comment(
    shanyrak_id: int,
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_shanyrak_or_404(shanyrak_id, db)
    comment = Comment(
        content=data.content,
        author_id=current_user.id,
        shanyrak_id=shanyrak_id,
    )
    db.add(comment)
    db.commit()
    return {"message": "Comment added successfully"}


# Таск 10: Получение списка комментариев
@router.get("/", response_model=CommentsListResponse)
def get_comments(shanyrak_id: int, db: Session = Depends(get_db)):
    _get_shanyrak_or_404(shanyrak_id, db)
    comments = (
        db.query(Comment)
        .filter(Comment.shanyrak_id == shanyrak_id)
        .order_by(Comment.created_at.desc())
        .all()
    )
    return CommentsListResponse(comments=comments)


# Таск 11: Изменение комментария
@router.patch("/{comment_id}")
def update_comment(
    shanyrak_id: int,
    comment_id: int,
    data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = _get_comment_or_404(comment_id, shanyrak_id, db)
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments",
        )
    comment.content = data.content
    db.commit()
    return {"message": "Comment updated successfully"}


# Таск 12: Удаление комментария
@router.delete("/{comment_id}")
def delete_comment(
    shanyrak_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = _get_comment_or_404(comment_id, shanyrak_id, db)
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments",
        )
    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}