from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from models.prompt import Prompt, PromptCategory

router = APIRouter()

class PromptCreate(BaseModel):
    original_text: str
    chinese_translation: Optional[str] = None
    category_id: int

class PromptUpdate(BaseModel):
    original_text: Optional[str] = None
    chinese_translation: Optional[str] = None
    category_id: Optional[int] = None

class PromptResponse(BaseModel):
    id: int
    original_text: str
    chinese_translation: Optional[str]
    category_id: int
    
    model_config = {
        "from_attributes": True
    }

class PaginatedResponse(BaseModel):
    results: List[PromptResponse]
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None

@router.post("/", response_model=PromptResponse)
async def create_prompt(prompt: PromptCreate, db: Session = Depends(get_db)):
    # 检查分类是否存在
    category = db.query(PromptCategory).filter(PromptCategory.id == prompt.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # 检查提示词原文是否重复
    existing_prompt = db.query(Prompt).filter(Prompt.original_text == prompt.original_text).first()
    if existing_prompt:
        raise HTTPException(status_code=400, detail="Original text already exists")
    
    db_prompt = Prompt(**prompt.dict())
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(prompt_id: int, prompt: PromptUpdate, db: Session = Depends(get_db)):
    db_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    update_data = prompt.dict(exclude_unset=True)
    
    # 如果要更新原文，检查是否重复
    if "original_text" in update_data:
        existing_prompt = db.query(Prompt).filter(
            Prompt.original_text == update_data["original_text"],
            Prompt.id != prompt_id
        ).first()
        if existing_prompt:
            raise HTTPException(status_code=400, detail="Original text already exists")
    
    # 如果要更新分类，检查分类是否存在
    if "category_id" in update_data:
        category = db.query(PromptCategory).filter(PromptCategory.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    for key, value in update_data.items():
        setattr(db_prompt, key, value)
    
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

@router.delete("/{prompt_id}")
async def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    db_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    db.delete(db_prompt)
    db.commit()
    return {"message": "Prompt deleted successfully"}

@router.get("/", response_model=PaginatedResponse)
async def get_prompts(
    db: Session = Depends(get_db),
    category_id: Optional[int] = None,
    original_text: Optional[str] = None,
    chinese_translation: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100)
):
    # 获取总数
    total_count = db.query(Prompt).count()
    
    query = db.query(Prompt)
    
    # 应用过滤条件
    if category_id is not None:
        # 获取当前分类及其所有子分类的ID
        subcategories = db.query(PromptCategory).filter(
            PromptCategory.parent_id == category_id
        ).all()
        category_ids = [category_id] + [c.id for c in subcategories]
        query = query.filter(Prompt.category_id.in_(category_ids))
    
    # 处理搜索条件
    search_text = original_text or search
    if search_text:
        query = query.filter(
            (Prompt.original_text.ilike(f"%{search_text}%")) |
            (Prompt.chinese_translation.ilike(f"%{search_text}%"))
        )
    
    # 应用分页
    prompts = query.offset(skip).limit(limit).all()
    
    # 构建分页响应
    next_url = None
    previous_url = None
    
    if skip + limit < total_count:
        next_params = f"?skip={skip + limit}&limit={limit}"
        if category_id:
            next_params += f"&category_id={category_id}"
        if original_text:
            next_params += f"&original_text={original_text}"
        if chinese_translation:
            next_params += f"&chinese_translation={chinese_translation}"
        next_url = f"/api/prompts/{next_params}"
    
    if skip > 0:
        previous_params = f"?skip={max(0, skip - limit)}&limit={limit}"
        if category_id:
            previous_params += f"&category_id={category_id}"
        if original_text:
            previous_params += f"&original_text={original_text}"
        if chinese_translation:
            previous_params += f"&chinese_translation={chinese_translation}"
        previous_url = f"/api/prompts{previous_params}"
    
    return PaginatedResponse(
        results=prompts,
        count=total_count,
        next=next_url,
        previous=previous_url
    )