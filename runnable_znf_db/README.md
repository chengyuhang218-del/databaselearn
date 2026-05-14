# HKZRSdb Demo：可直接运行的 ZNF 数据库教学版

这是根据老师的 `krab_DB-master` 项目整理出的版本。

它不依赖 Flask、SQLAlchemy、PostgreSQL 或 pandas，只使用 Python 标准库：

- `http.server`：提供网页服务。
- `sqlite3`：创建本地数据库。
- `json`：保存表达量、UniProt feature、gene structure 等结构化信息。

## 一键运行

```bash
cd /Users/chengyuhang2/Documents/Codex/2026-05-13/users-chengyuhang2-desktop-pdf-users-chengyuhang2/runnable_znf_db
python3 app.py
```

然后访问：

```text
http://127.0.0.1:5050
```

## 模拟配置

配置在 `config.py` 中：

```python
DEMO_DB = {
    "driver": "sqlite3",
    "host": "localhost",
    "port": "0",
    "database": "data/znf_demo.sqlite3",
    "user": "znf_demo_user",
    "password": "znf_demo_pass_123",
}
```

这个账号密码只是模拟值。SQLite 实际不需要用户名和密码，但这样写可以帮助你理解 PostgreSQL 版本里连接配置应该放在哪里。

## 数据库文件

第一次运行时会自动生成：

```text
runnable_znf_db/data/znf_demo.sqlite3
```

里面会自动写入 3 个 ZNF、3 个 ChIP-seq dataset、4 个 repeat 和若干 peak / repeat region / expression / ortholog 模拟数据。

## 页面

- `/`：首页和统计信息。
- `/kzfp`：ZNF 总览。
- `/repeat`：Repeat 总览。
- `/znf?symbol=ZNF197`：单个 ZNF 详情。
- `/repeat_one?id=1`：单个 repeat 详情。
- `/about`：路径、账号、密码配置说明。

## JSON API

- `/api/znfs`
- `/api/repeats`
- `/api/peaks`

## 与老师原项目的对应关系

| 老师项目 | 这个可运行版 | 说明 |
|---|---|---|
| `ZFWebDatabase.py` | `database.py` | 建表、连接数据库、插入示例数据 |
| `routes.py` | `app.py` | 网页路由和 API |
| PostgreSQL | SQLite | 为了本地直接跑通 |
| `/home/luozhihui/...` | `runnable_znf_db/data/` | 路径改为项目内相对路径 |
| `luozh / luozh123 / ZNFdb` | `znf_demo_user / znf_demo_pass_123 / znf_demo.sqlite3` | 改成模拟配置 |


## 后续接真实数据

后续可以接真实数据，建议按这个顺序替换：

1. 保留 `app.py` 的网页查询逻辑。
2. 保留 `database.py` 的表结构。
3. 把 `seed_db()` 中的模拟数据替换成真实导入函数。
4. 将老师项目中 `import_data.py` 的路径改成 `Path(DATA_DIR) / ...` 形式。
5. 先导入 1 个 ZNF 的小样本，确认页面能查到，再导入完整数据。
