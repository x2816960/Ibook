from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

engine = None
SessionLocal = None


def init_db():
    """初始化数据库引擎和会话工厂"""
    global engine, SessionLocal
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def recreate_engine():
    """重新创建数据库引擎（用于导入备份后刷新连接）"""
    global engine, SessionLocal
    if engine:
        engine.dispose()  # 关闭所有连接
    init_db()


class Base(DeclarativeBase):
    pass


# 初始化数据库
init_db()
