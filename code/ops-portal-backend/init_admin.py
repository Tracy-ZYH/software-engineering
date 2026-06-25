"""
初始化管理员账号脚本
运行方式：python init_admin.py
"""
from app.database import SessionLocal
from app.models.account import OpsAccount, AccountRole, AccountStatus
from app.utils.auth import hash_password


def init_admin():
    db = SessionLocal()
    try:
        # 检查是否已存在 admin 账号
        existing = db.query(OpsAccount).filter(OpsAccount.username == "admin").first()
        if existing:
            print("⚠️  管理员账号 'admin' 已存在，如需重置密码请先删除该账号")
            return

        admin = OpsAccount(
            username="admin",
            password=hash_password("admin123"),  # 密码：admin123
            real_name="系统管理员",
            phone="13800000000",
            email="admin@ops.com",
            department="技术部",
            role=AccountRole.ADMIN,
            status=AccountStatus.ACTIVE,
        )
        db.add(admin)
        db.commit()
        print("✅ 管理员账号创建成功")
        print("   用户名: admin")
        print("   密码:   admin123")
        print("   角色:   管理员")
    except Exception as e:
        db.rollback()
        print(f"❌ 创建失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_admin()
