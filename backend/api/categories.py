from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from models.prompt import PromptCategory, Prompt

router = APIRouter()

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None

class CategoryUpdate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    parent_id: Optional[int]
    is_default: bool
    children: List['CategoryResponse'] = []

    class Config:
        orm_mode = True

CategoryResponse.update_forward_refs()

@router.post("/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    # 检查分类名是否重复
    if db.query(PromptCategory).filter(PromptCategory.name == category.name).first():
        raise HTTPException(status_code=400, detail="分类名称已存在")
    
    # 如果有父级分类，检查父级分类是否存在且不是默认分类
    if category.parent_id:
        parent = db.query(PromptCategory).filter(PromptCategory.id == category.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="父级分类不存在")
        if parent.is_default:
            raise HTTPException(status_code=400, detail="不能在默认分类下创建子分类")
    
    db_category = PromptCategory(
        name=category.name,
        parent_id=category.parent_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    db_category = db.query(PromptCategory).filter(PromptCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    if db_category.is_default:
        raise HTTPException(status_code=400, detail="不能修改默认分类")
    
    # 检查新名称是否与其他分类重复
    if db.query(PromptCategory).filter(
        and_(
            PromptCategory.name == category.name,
            PromptCategory.id != category_id
        )
    ).first():
        raise HTTPException(status_code=400, detail="分类名称已存在")
    
    db_category.name = category.name
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(PromptCategory).filter(PromptCategory.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    if db_category.is_default:
        raise HTTPException(status_code=400, detail="不能删除默认分类")
    
    # 获取默认分类
    default_category = db.query(PromptCategory).filter(PromptCategory.is_default == True).first()
    
    # 将该分类及其子分类下的所有提示词移动到默认分类
    child_categories = db.query(PromptCategory).filter(PromptCategory.parent_id == category_id).all()
    category_ids = [category_id] + [cat.id for cat in child_categories]
    
    db.query(Prompt).filter(Prompt.category_id.in_(category_ids)).update(
        {Prompt.category_id: default_category.id},
        synchronize_session=False
    )
    
    # 删除子分类
    for child in child_categories:
        db.delete(child)
    
    # 删除当前分类
    db.delete(db_category)
    db.commit()
    return {"message": "分类删除成功"}

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    # 获取所有顶级分类（包括默认分类）
    root_categories = db.query(PromptCategory).filter(PromptCategory.parent_id == None).all()
    
    def build_category_tree(categories):
        result = []
        for category in categories:
            # 递归获取子分类
            children = db.query(PromptCategory).filter(PromptCategory.parent_id == category.id).all()
            category_dict = CategoryResponse(
                id=category.id,
                name=category.name,
                parent_id=category.parent_id,
                is_default=category.is_default,
                children=build_category_tree(children)
            )
            result.append(category_dict)
        return result
    
    return build_category_tree(root_categories)