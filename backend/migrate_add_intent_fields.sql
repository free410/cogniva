-- 迁移脚本：添加意图相关性验证字段到 citations 表
-- 运行方式: psql -U postgres -d your_database -f migrate_add_intent_fields.sql

-- 检查字段是否已存在，不存在则添加
DO $$
BEGIN
    -- intent_match_ratio
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'citations' AND column_name = 'intent_match_ratio'
    ) THEN
        ALTER TABLE citations ADD COLUMN intent_match_ratio FLOAT;
    END IF;
    
    -- topic_match
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'citations' AND column_name = 'topic_match'
    ) THEN
        ALTER TABLE citations ADD COLUMN topic_match BOOLEAN;
    END IF;
    
    -- entity_match_score
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'citations' AND column_name = 'entity_match_score'
    ) THEN
        ALTER TABLE citations ADD COLUMN entity_match_score FLOAT;
    END IF;
    
    -- term_match_score
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'citations' AND column_name = 'term_match_score'
    ) THEN
        ALTER TABLE citations ADD COLUMN term_match_score FLOAT;
    END IF;
    
    -- matched_entities
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'citations' AND column_name = 'matched_entities'
    ) THEN
        ALTER TABLE citations ADD COLUMN matched_entities JSONB;
    END IF;
    
    RAISE NOTICE 'Migration completed successfully!';
END
$$;
