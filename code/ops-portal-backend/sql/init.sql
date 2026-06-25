-- ============================================================
-- 运维数字员工 - 数据库建表脚本
-- 数据库名称：ops_portal
-- ============================================================

CREATE DATABASE IF NOT EXISTS ops_portal
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE ops_portal;

-- ------------------------------------------------------------
-- 1. 运维账号表 (ops_account)
--    存储运维人员和管理员的账号信息
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ops_account (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码（bcrypt加密）',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    phone VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    email VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    department VARCHAR(100) DEFAULT NULL COMMENT '所属部门',
    role ENUM('admin', 'operator') NOT NULL DEFAULT 'operator' COMMENT '角色：admin=管理员, operator=运维人员',
    status ENUM('active', 'frozen') NOT NULL DEFAULT 'active' COMMENT '状态：active=正常, frozen=冻结',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_status (status),
    INDEX idx_role (role),
    INDEX idx_department (department)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='运维账号表';

-- ------------------------------------------------------------
-- 2. 工单/在线记录表 (ops_ticket)
--    用户提问后RAG无法回答时生成的工单
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ops_ticket (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    question TEXT NOT NULL COMMENT '用户问题',
    rag_answer TEXT DEFAULT NULL COMMENT 'RAG返回的答案（可能为空）',
    status ENUM('pending', 'processing', 'resolved', 'closed') NOT NULL DEFAULT 'pending' COMMENT '状态：pending=待处理, processing=处理中, resolved=已解决, closed=已关闭',
    created_by VARCHAR(100) NOT NULL COMMENT '报障人姓名/标识',
    contact_info VARCHAR(100) DEFAULT NULL COMMENT '报障人联系方式',
    resolver_id INT DEFAULT NULL COMMENT '处理人ID（关联ops_account）',
    resolution TEXT DEFAULT NULL COMMENT '处理方案',
    is_added_to_kb TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已录入知识库：0=否, 1=是',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    resolved_at DATETIME DEFAULT NULL COMMENT '处理完成时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_status (status),
    INDEX idx_resolver (resolver_id),
    INDEX idx_added_to_kb (is_added_to_kb),
    CONSTRAINT fk_ticket_resolver FOREIGN KEY (resolver_id) REFERENCES ops_account(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工单/在线记录表';

-- ------------------------------------------------------------
-- 3. 知识库条目表 (ops_knowledge)
--    记录已录入RAG的知识条目，与AnythingLLM同步
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ops_knowledge (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    question TEXT NOT NULL COMMENT '问题',
    answer TEXT NOT NULL COMMENT '答案/解决方案',
    category VARCHAR(50) DEFAULT NULL COMMENT '分类',
    source ENUM('manual', 'ticket') NOT NULL DEFAULT 'manual' COMMENT '来源：manual=手动录入, ticket=工单转换',
    source_ticket_id INT DEFAULT NULL COMMENT '来源工单ID（当source=ticket时）',
    created_by INT DEFAULT NULL COMMENT '创建人ID（关联ops_account）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_category (category),
    INDEX idx_source (source),
    CONSTRAINT fk_knowledge_ticket FOREIGN KEY (source_ticket_id) REFERENCES ops_ticket(id) ON DELETE SET NULL,
    CONSTRAINT fk_knowledge_creator FOREIGN KEY (created_by) REFERENCES ops_account(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库条目表';

-- ------------------------------------------------------------
-- 4. 操作日志表 (ops_operation_log)
--    记录所有关键操作的审计日志
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ops_operation_log (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    operator_id INT DEFAULT NULL COMMENT '操作人ID（关联ops_account）',
    action VARCHAR(50) NOT NULL COMMENT '操作类型：CREATE/UPDATE/DELETE/FREEZE/UNFREEZE/LOGIN',
    target_type VARCHAR(50) NOT NULL COMMENT '操作对象类型：ACCOUNT/TICKET/KNOWLEDGE',
    target_id INT DEFAULT NULL COMMENT '操作对象ID',
    detail TEXT DEFAULT NULL COMMENT '操作详情',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    INDEX idx_operator (operator_id),
    INDEX idx_target (target_type, target_id),
    INDEX idx_created_at (created_at),
    CONSTRAINT fk_log_operator FOREIGN KEY (operator_id) REFERENCES ops_account(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';
