from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "znf_demo.sqlite3"

DEMO_DB = {
    "driver": "sqlite3",
    "host": "localhost",
    "port": "0",
    "database": str(DATABASE_PATH),
    "user": "znf_demo_user",
    "password": "znf_demo_pass_123",
}

PROJECT_INFO = {
    "name": "HKZRSdb Demo",
    "full_name": "Human KRAB-ZFPs & Repetitive Sequences Database Demo",
    "source_note": "教学复现版：使用本地 SQLite 与模拟数据，保留老师项目的数据结构和网页查询逻辑。",
}
