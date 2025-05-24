-- 创建提示词分类表
CREATE TABLE prompt_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    parent_id INTEGER REFERENCES prompt_categories(id),
    is_default BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_parent CHECK (
        (is_default = true AND parent_id IS NULL) OR
        (is_default = false)
    )
);

-- 创建默认分类
INSERT INTO prompt_categories (name, is_default) VALUES ('默认分类', true);

-- 创建提示词表
CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    original_text TEXT NOT NULL,
    chinese_translation TEXT,
    category_id INTEGER NOT NULL REFERENCES prompt_categories(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建提示词方案表
CREATE TABLE prompt_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 在原有表结构后添加以下索引

-- prompts表索引
-- 提示词原文唯一索引
CREATE UNIQUE INDEX idx_prompts_original_text ON prompts(original_text);
-- 分类ID索引（用于按分类查询）
CREATE INDEX idx_prompts_category_id ON prompts(category_id);
-- 提示词原文和中文翻译的文本搜索索引
CREATE INDEX idx_prompts_original_text_search ON prompts USING gin(to_tsvector('english', original_text));
CREATE INDEX idx_prompts_chinese_translation_search ON prompts USING gin(to_tsvector('simple', chinese_translation));

-- 创建更新时间触发器
CREATE TRIGGER update_prompt_categories_updated_at
    BEFORE UPDATE ON prompt_categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prompts_updated_at
    BEFORE UPDATE ON prompts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- prompt_templates表索引
-- 方案名称唯一索引
CREATE UNIQUE INDEX idx_prompt_templates_name ON prompt_templates(name);
-- 更新时间索引（用于排序）
CREATE INDEX idx_prompt_templates_updated_at ON prompt_templates(updated_at DESC);
CREATE TRIGGER update_prompt_templates_updated_at
    BEFORE UPDATE ON prompt_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();