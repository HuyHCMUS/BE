# app/api/v1/vocabulary.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.services.auth import get_current_user
from sqlalchemy.exc import SQLAlchemyError
import datetime
import base64
import io
from PIL import Image
import uuid
import os


from app.models.vocabulary import vocabList, vocabItem
from app.schemas.vocabulary import VocabListSchema, vocabItemSchema


router = APIRouter()

# Vocabulary list
@router.get("/vocabulary-list", response_model=dict)
async def getVocabList(current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    try:

        List = db.query(vocabList).filter(or_(
            vocabList.list_id < 0,  # Điều kiện 1: id = 0
            vocabList.user_id == current_user_id  # Điều kiện 2: user_id khớp với current_user_id
        )
        ).all()

        vocab_list_user = []
        vocab_list_public = []
        for item in List:
            vocab_list = {
                "list_id": item.list_id,
                "title": item.title,
                "category": item.category,
                "description": item.description,
                "total_words": item.total_words,
                "progress": item.progress or 0,
                "updated_at": item.updated_at,
                "image": item.image 
            }
            if vocab_list['list_id'] < 0:
               vocab_list_public.append(vocab_list)
            else: vocab_list_user.append(vocab_list) 

        return {
            "status": 200,
            "message": "Vocabulary list retrieved successfully",
            "data": {
                'vocab_list_user': vocab_list_user,
                'vocab_list_public':vocab_list_public  
                }
        }
    except SQLAlchemyError as e:
        print(f"SQLAlchemy error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.post("/vocabulary", response_model=dict)
async def create_vocab_list(
    vocab_in: VocabListSchema, 
    current_user_id: int = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    try:
        # Print debugging information
        print(f"Creating vocabulary list with user_id: {current_user_id}")
        print(f"Input data: {vocab_in.dict()}")
        # Create new vocabulary list
        new_vocab = vocabList(
            title=vocab_in.title,
            user_id=current_user_id,
            category=vocab_in.category,
            description=vocab_in.description,
        )
        if vocab_in.image_base64:
            if "base64," in vocab_in.image_base64:
                base64_data = vocab_in.image_base64.split("base64,")[1]
            else:
                base64_data = vocab_in.image_base64
            img_data = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(img_data))
            file_name = f"{uuid.uuid4()}.png"
            file_path = os.path.join("static/images", file_name)
            print(file_path)
            image.save(file_path)
            image_url = f"http://localhost:8000/static/images/{file_name}"
            new_vocab.image = image_url
        
        # print(f"Created vocab object: {new_vocab.__dict__}")
        
        db.add(new_vocab)
        db.commit()
        db.refresh(new_vocab)
        
        return {
            "status": 200,
            "message": "Vocabulary list created successfully",
            "data": 0
        }
    except SQLAlchemyError as e:
        print(f"SQLAlchemy error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
   
@router.patch("/vocabulary", response_model=dict)
async def edit_vocab_list(
    vocab_in: VocabListSchema, 
    current_user_id: int = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    try:
        if vocab_in.list_id < 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit a public vocabulary list"
            )
        # Find the vocabulary list to update
        vocab = db.query(vocabList).filter(vocabList.list_id == vocab_in.list_id,vocabList.user_id == current_user_id).first()
        if not vocab:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocabulary list not found"
            )
        
        if vocab_in.image_base64:
            if "base64," in vocab_in.image_base64:
                base64_data = vocab_in.image_base64.split("base64,")[1]
            else:
                base64_data = vocab_in.image_base64
            img_data = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(img_data))
            file_name = f"{uuid.uuid4()}.png"
            file_path = os.path.join("static/images", file_name)
            print(file_path)
            image.save(file_path)
            image_url = f"http://localhost:8000/static/images/{file_name}"
            vocab.image = image_url
        
        # Update the vocabulary list
        vocab.title = vocab_in.title
        vocab.category = vocab_in.category
        vocab.description = vocab_in.description
        vocab.updated_at = datetime.datetime.utcnow()

        db.commit()
        db.refresh(vocab)
        
        
        return {
            "status": 200,
            "message": "Vocabulary list updated successfully",
            "data": 0
        }
    except SQLAlchemyError as e:
        print(f"SQLAlchemy error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.delete("/vocabulary/{list_id}", response_model=dict)
async def delete_vocab_list(list_id: int, 
                            current_user_id: int = Depends(get_current_user), 
                            db: Session = Depends(get_db)):
    try:
        if list_id < 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete a public vocabulary list"
            )
        # Find the vocabulary list to delete
        vocab = db.query(vocabList).filter(vocabList.list_id == list_id, vocabList.user_id == current_user_id).first()
        if not vocab:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocabulary list not found"
            )
        
        # Delete the vocabulary list
        db.delete(vocab)
        db.commit()
        
        return {
            "status": 200,
            "message": "Vocabulary list deleted successfully",
            "data": 0
        }
    except SQLAlchemyError as e:
        print(f"SQLAlchemy error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

# Vocabulary item
@router.get("/vocabulary-item/{list_id}", response_model=dict)
async def get_list_item(list_id: int, 
                        current_user_id: int = Depends(get_current_user), 
                        db: Session = Depends(get_db)):
    try:
        # Find the vocabulary list
        vocab = db.query(vocabList).filter(vocabList.list_id == list_id, vocabList.user_id == current_user_id).first()
        if not vocab:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocabulary list not found"
            )
        
        # Find the vocabulary items
        items = db.query(vocabItem).filter(vocabItem.list_id == list_id).all()
        vocab_items = []
        for item in items:
            vocab_items.append({
                "item_id": item.item_id,
                "list_id": item.list_id,
                "word": item.word,
                "ipa": item.ipa,
                "definition": item.definition,
                "example": item.example,
                "image_url": item.image_url,
            })
        #print(f"Vocabulary items: {vocab_items}")
        return {
            "status": 200,
            "message": "Vocabulary list retrieved successfully",
            "data": vocab_items
        }
    except SQLAlchemyError as e:
        print(f"SQLAlchemy error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.post("/vocabulary-item", response_model=dict)
async def create_vocab_item(
    vocab_in: vocabItemSchema,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Find the vocabulary list
        # print('xxx')
        # print('vocab_inss', vocab_in)
        vocab = db.query(vocabList).filter(vocabList.list_id == vocab_in.list_id, vocabList.user_id == current_user_id).first()
        if not vocab:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocabulary list not found"
            )
        new_item = vocabItem(
            list_id=vocab_in.list_id,
            word=vocab_in.word,
            definition=vocab_in.definition,
            example=vocab_in.example,
            ipa=vocab_in.ipa,
        )
        # print(vocab_in.image_base64,'ccc')
        if vocab_in.image_base64:
            if "base64," in vocab_in.image_base64:
                base64_data = vocab_in.image_base64.split("base64,")[1]
            else:
                base64_data = vocab_in.image_base64
            img_data = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(img_data))
            file_name = f"{uuid.uuid4()}.png"
            file_path = os.path.join("static/images", file_name)
            print(file_path)
            image.save(file_path)
            image_url = f"http://localhost:8000/static/images/{file_name}"
            new_item.image_url = image_url
        vocab.total_words += 1
        vocab.updated_at = datetime.datetime.utcnow()
        # Create new vocabulary item


        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        return {
            "status": 200,
            "message": "Vocabulary item created successfully",
            "data": 0
        }
    except SQLAlchemyError as e:
        print(f"SQLAlchemy error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )   

@router.patch("/vocabulary-item", response_model=dict)
async def edit_vocab_item(
    vocab_in: vocabItemSchema, 
    current_user_id: int = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    try:
        # Find the list item to update
        # print('vocab_in', vocab_in)
        list = db.query(vocabList).filter(vocabList.list_id == vocab_in.list_id, vocabList.user_id == current_user_id).first()
        if not list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocabulary list not found"
            )
        list.updated_at = datetime.datetime.utcnow()
        
        # Find the vocabulary item to update
        vocab = db.query(vocabItem).filter(vocabItem.item_id == vocab_in.item_id).first()
        if not vocab:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocabulary item not found"
            )
        if vocab_in.image_base64:
            if "base64," in vocab_in.image_base64:
                base64_data = vocab_in.image_base64.split("base64,")[1]
            else:
                base64_data = vocab_in.image_base64
            img_data = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(img_data))
            file_name = f"{uuid.uuid4()}.png"
            file_path = os.path.join("static/images", file_name)
            print(file_path)
            image.save(file_path)
            image_url = f"http://localhost:8000/static/images/{file_name}"
            vocab.image_url = image_url
        # Update the vocabulary item
        vocab.word = vocab_in.word
        vocab.definition = vocab_in.definition
        vocab.example = vocab_in.example
        vocab.ipa = vocab_in.ipa
        #vocab.updated_at = datetime.datetime.utcnow()

        db.commit()
        db.refresh(vocab)
        
        return {
            "status": 200,
            "message": "Vocabulary item updated successfully",
            "data": 0
        }
    except SQLAlchemyError as e:
        print(f"SQLAlchemy error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.delete("/vocabulary-item/{item_id}", response_model=dict)
async def delete_vocab_item(item_id: int,
                            current_user_id: int = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    try:

        # Find the vocabulary item to delete
        item = db.query(vocabItem).filter(vocabItem.item_id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocabulary item not found"
            )
        
        # Find the vocabulary list
        vocab = db.query(vocabList).filter(vocabList.list_id == item.list_id, vocabList.user_id == current_user_id).first()
        if not vocab:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocabulary list not found"
            )
        vocab.total_words -= 1
        vocab.updated_at = datetime.datetime.utcnow()
        # Delete the vocabulary item
        db.delete(item)
        db.commit()
        
        return {
            "status": 200,
            "message": "Vocabulary item deleted successfully",
            "data": 0
        }
    except SQLAlchemyError as e:
        print(f"SQLAlchemy error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    