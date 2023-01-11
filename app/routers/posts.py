from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from .. import database, models, schemas, oauth2

router = APIRouter()


@router.get("/", response_model=list[schemas.PostResponse])
def get_posts(db: Session = Depends(database.get_db),
              limit: int = 10, skip: int = 0, search: str = "") -> list[schemas.PostResponse]:
    all_posts = db.query(models.Post, func.count(models.Rating.post_id).label("likes"))\
        .join(models.Rating, models.Rating.post_id == models.Post.id, isouter=True)\
        .group_by(models.Post.id)\
        .filter(models.Post.title.contains(search), models.Post.published == "TRUE")\
        .order_by(desc(models.Post.created_at))\
        .limit(limit).offset(skip).all()
    return all_posts


@router.get("/my", response_model=list[schemas.PostResponse])
def get_posts_my(db: Session = Depends(database.get_db),
                 verified_user: models.User = Depends(oauth2.verify_current_user),
                 limit: int = 10, skip: int = 0, search: str = "") -> list[schemas.PostResponse]:
    my_posts = db.query(models.Post, func.count(models.Rating.post_id).label("likes"))\
        .join(models.Rating, models.Rating.post_id == models.Post.id, isouter=True)\
        .group_by(models.Post.id)\
        .filter(models.Post.title.contains(search), models.Post.owner_id == verified_user.id)\
        .order_by(desc(models.Post.created_at))\
        .limit(limit).offset(skip).all()
    return my_posts


@router.get("/latest", response_model=schemas.PostResponse)
def get_latest_post(db: Session = Depends(database.get_db)) -> schemas.PostResponse:
    latest_post = db.query(models.Post, func.count(models.Rating.post_id).label("likes"))\
        .join(models.Rating, models.Rating.post_id == models.Post.id, isouter=True)\
        .group_by(models.Post.id)\
        .filter(models.Post.published == "TRUE")\
        .order_by(desc(models.Post.created_at)).first()
    return latest_post


@router.get("/{id_}", response_model=schemas.PostResponse)
def get_post(id_: int, db: Session = Depends(database.get_db),
             verified_user: models.User = Depends(oauth2.verify_current_user)) -> schemas.PostResponse:
    found_post = db.query(models.Post, func.count(models.Rating.post_id).label("likes"))\
        .join(models.Rating, models.Rating.post_id == models.Post.id, isouter=True)\
        .group_by(models.Post.id)\
        .filter(models.Post.id == id_).first()
    if found_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post was not found (id: {id_})")
    if found_post.Post.published is False and found_post.Post.owner_id != verified_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post was not found (id: {id_})")
    return found_post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(database.get_db),
                verified_user: models.User = Depends(oauth2.verify_current_user)) -> schemas.Post:
    created_post = models.Post(**dict(post), owner_id=verified_user.id)
    db.add(created_post)
    db.commit()
    db.refresh(created_post)
    return created_post


@router.put("/publish/{id_}")
def change_post_visibility(id_: int, db: Session = Depends(database.get_db),
                           verified_user: models.User = Depends(oauth2.verify_current_user)) -> dict:
    post = db.query(models.Post).filter(models.Post.id == id_)
    fetched_post = post.first()
    if fetched_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post was not found (id: {id_})")
    if fetched_post.owner_id != verified_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="unauthorized action")
    updated_post = schemas.PostCreate(title=fetched_post.title, content=fetched_post.content,
                                      published=not fetched_post.published)
    post.update(dict(updated_post), synchronize_session=False)
    db.commit()
    return {"detail": f"post was successfully {'' if updated_post.published else 'un'}published (id: {id_})"}


@router.delete("/{id_}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id_: int, db: Session = Depends(database.get_db),
                verified_user: models.User = Depends(oauth2.verify_current_user)) -> Response:
    post_to_delete = db.query(models.Post).filter(models.Post.id == id_)
    post = post_to_delete.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post was not found (id: {id_})")
    if post.owner_id != verified_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="unauthorized action")
    post_to_delete.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id_}", response_model=schemas.PostResponse)
def update_post(id_: int, post: schemas.PostCreate, db: Session = Depends(database.get_db),
                verified_user: models.User = Depends(oauth2.verify_current_user)) -> schemas.PostResponse:
    post_to_update = db.query(models.Post).filter_by(id=id_)
    fetched_post = post_to_update.first()
    if fetched_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post was not found (id: {id_})")
    if fetched_post.owner_id != verified_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="unauthorized action")
    post_to_update.update(dict(post), synchronize_session=False)
    db.commit()
    post_to_update = db.query(models.Post, func.count(models.Rating.post_id).label("likes"))\
        .join(models.Rating, models.Rating.post_id == models.Post.id, isouter=True)\
        .group_by(models.Post.id)\
        .filter(models.Post.id == id_).first()
    return post_to_update
