from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.base import BaseModel

class PromptCategory(BaseModel):
    __tablename__ = "prompt_categories"

    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("prompt_categories.id"))
    is_default = Column(Boolean, nullable=False, default=False)

    # 关系
    parent = relationship("PromptCategory",
                         backref="children",
                         remote_side="[PromptCategory.id]")
    prompts = relationship("Prompt", back_populates="category")

class Prompt(BaseModel):
    __tablename__ = "prompts"

    original_text = Column(Text, nullable=False)
    chinese_translation = Column(Text)
    category_id = Column(Integer, ForeignKey("prompt_categories.id"), nullable=False)

    # 关系
    category = relationship("PromptCategory", back_populates="prompts")

class PromptTemplate(BaseModel):
    __tablename__ = "prompt_templates"

    name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)