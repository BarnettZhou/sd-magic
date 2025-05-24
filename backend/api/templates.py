from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from database import get_db
from models.prompt import PromptTemplate

router = APIRouter()

class PromptTemplateCreate(BaseModel):
    name: str
    content: str

class PromptTemplateUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None

class PromptTemplateResponse(BaseModel):
    id: int
    name: str
    content: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }

@router.post("/", response_model=PromptTemplateResponse)
async def create_template(template: PromptTemplateCreate, db: Session = Depends(get_db)):
    # 检查方案名称是否重复
    existing_template = db.query(PromptTemplate).filter(PromptTemplate.name == template.name).first()
    if existing_template:
        raise HTTPException(status_code=400, detail="Template name already exists")
    
    db_template = PromptTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.put("/{template_id}", response_model=PromptTemplateResponse)
async def update_template(template_id: int, template: PromptTemplateUpdate, db: Session = Depends(get_db)):
    db_template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # 如果更新名称，检查是否重复
    if template.name is not None and template.name != db_template.name:
        existing_template = db.query(PromptTemplate).filter(PromptTemplate.name == template.name).first()
        if existing_template:
            raise HTTPException(status_code=400, detail="Template name already exists")
    
    for key, value in template.dict(exclude_unset=True).items():
        setattr(db_template, key, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template

@router.delete("/{template_id}")
async def delete_template(template_id: int, db: Session = Depends(get_db)):
    db_template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(db_template)
    db.commit()
    return {"message": "Template deleted successfully"}

@router.get("/", response_model=List[PromptTemplateResponse])
async def list_templates(
    name: Optional[str] = None,
    page: int = Query(1, gt=0),
    db: Session = Depends(get_db)
):
    query = db.query(PromptTemplate)
    
    # 按名称筛选
    if name:
        query = query.filter(PromptTemplate.name.ilike(f"%{name}%"))
    
    # 按更新时间倒序排序
    query = query.order_by(PromptTemplate.updated_at.desc())
    
    # 分页
    per_page = 20
    offset = (page - 1) * per_page
    templates = query.offset(offset).limit(per_page).all()
    
    return templates