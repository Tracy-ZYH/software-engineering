-- ============================================================
-- 初始数据脚本
-- ============================================================
USE ops_portal;

-- 插入默认管理员账号
-- 密码：admin123 (bcrypt 加密)
-- 如需修改密码，可以在启动后调用登录接口验证
INSERT INTO ops_account (username, password, real_name, phone, email, department, role, status) VALUES
('admin', '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5Gzq5Gzq5Gzq5Gzq5Gzq5Gzq', '系统管理员', '13800000000', 'admin@ops.com', '技术部', 'admin', 'active')
ON DUPLICATE KEY UPDATE username = username;

-- 注意：上面bcrypt哈希是占位符，项目首次启动时建议通过注册接口创建管理员
-- 建议启动后通过API注册admin账号，或用下面方式生成正确的bcrypt密码
-- Python生成方式:
--   from passlib.hash import bcrypt
--   print(bcrypt.hash("admin123"))
