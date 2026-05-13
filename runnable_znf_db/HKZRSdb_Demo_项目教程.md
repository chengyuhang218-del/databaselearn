# HKZRSdb Demo 项目教程：从零理解并运行 ZNF 数据库

> 项目路径：`/Users/chengyuhang2/Desktop/runnable_znf_db`  
> 教程目标：从环境准备、运行入口、数据库结构、页面路由、API 到源码逐行解释，完整理解这个可运行的 ZNF 数据库教学版。

## 1. 项目是什么

这个项目是一个“开箱即跑”的 ZNF / KRAB-ZFP 数据库教学演示版。它用 Python 标准库实现了一个本地网页服务，并用 SQLite 保存模拟数据。运行后，你可以在浏览器里查看 ZNF 基因、ChIP-seq 数据集、peak、repeat、表达量、基因结构和 ortholog 信息。

项目没有使用 Flask、Django、SQLAlchemy、pandas 等第三方库，核心目的是让数据库建表、插入数据、查询数据、渲染网页这条链路变得清楚。

## 2. 目录结构

```text
runnable_znf_db/
├── README.md                 # 项目原始说明文档
├── app.py                    # Web 服务入口、页面路由、HTML 渲染、JSON API
├── config.py                 # 路径、数据库模拟配置、项目信息
├── database.py               # SQLite 连接、建表、插入模拟数据、查询辅助函数
└── data/
    └── znf_demo.sqlite3      # 本地 SQLite 数据库文件，运行时自动创建或复用
```

## 3. 从零运行

### 3.1 进入项目目录

```bash
cd /Users/chengyuhang2/Desktop/runnable_znf_db
```

### 3.2 启动服务

```bash
python3 app.py
```

终端看到下面内容就说明启动成功：

```text
HKZRSdb demo is running at http://127.0.0.1:5050
Press Ctrl+C to stop.
```

### 3.3 打开页面

浏览器访问：

```text
http://127.0.0.1:5050
```

可以继续访问这些页面：

| 地址 | 作用 |
|---|---|
| `/` | 首页，展示数据库统计与搜索框 |
| `/kzfp` | ZNF / KZFP 总览表 |
| `/repeat` | Repeat 总览表 |
| `/znf?symbol=ZNF197` | 单个 ZNF 详情页 |
| `/repeat_one?id=1` | 单个 repeat 详情页 |
| `/about` | 配置说明页 |
| `/api/znfs` | ZNF JSON 数据 |
| `/api/repeats` | Repeat JSON 数据 |
| `/api/peaks` | Peak JSON 数据 |

## 4. 程序整体执行流程

```text
用户执行 python3 app.py
        ↓
app.py 调用 main()
        ↓
main() 调用 init_db()
        ↓
database.py 建表并插入模拟数据
        ↓
ThreadingHTTPServer 监听 127.0.0.1:5050
        ↓
浏览器访问不同 URL
        ↓
Handler.do_GET() 判断路径
        ↓
调用 home() / kzfp() / znf_detail() 等页面函数
        ↓
页面函数调用 row() / rows() 查询 SQLite
        ↓
page() 包装 HTML 并返回给浏览器
```

## 5. 数据库表说明

| 表名 | 作用 | 关键字段 |
|---|---|---|
| `znf` | 保存 ZNF 基因基础信息 | `gene_symbol`, `ensembl`, `zinc_finger` |
| `chip_data` | 保存 ChIP-seq 数据集信息 | `data_name`, `data_source`, `znf_gene_symbol` |
| `repeat` | 保存 repeat 分类信息 | `repeat_name`, `sub_family`, `main_family` |
| `peak` | 保存 peak 与 repeat overlap 后的结果 | `chr`, `start`, `end`, `repeat_name` |
| `repeat_region` | 保存 repeat 区域坐标 | `chr`, `start`, `end`, `znf_gene_symbol` |
| `motif` | 保存 motif 示例字符串 | `chip_data_name`, `raw_motif` |
| `expression` | 保存表达量模拟数据 | `ensembl`, `cell_lines`, `values_json` |
| `gene_structure` | 保存基因结构 JSON | `ensembl`, `structure_json` |
| `ortholog` | 保存同源基因信息 | `scientific_name`, `ortholog_gene_name` |

## 6. 模块职责

### 6.1 config.py

`config.py` 只负责配置，不负责业务逻辑。它把项目根目录、数据目录、数据库路径、模拟数据库账号和页面项目名集中放在一个地方。这样以后如果要从 SQLite 换成 PostgreSQL，或者要换数据目录，优先改这里。

### 6.2 database.py

`database.py` 是数据层。它负责创建 SQLite 连接、定义建表 SQL、准备模拟数据、第一次运行时插入种子数据，并提供 `row()` 和 `rows()` 两个查询辅助函数。

### 6.3 app.py

`app.py` 是应用入口和页面层。它负责启动 HTTP 服务、解析浏览器 URL、根据路由调用不同页面函数、查询数据库、拼接 HTML、返回 JSON API。

## 7. 常见修改方法

### 7.1 增加一个新的 ZNF

打开 `database.py`，在 `SAMPLE_ZNFS` 中追加一个字典，并在 `SAMPLE_CHIPS`、`SAMPLE_PEAKS` 中补充对应数据。删除旧的 `data/znf_demo.sqlite3` 后重新运行 `python3 app.py`，数据库会按新数据重新初始化。

### 7.2 增加一个新页面

在 `app.py` 中新增一个函数，例如 `def motif_page(): ...`，然后在 `Handler.do_GET()` 里增加一个路径判断，例如 `if path == "/motif": ...`。

### 7.3 接入真实数据库

教学版为了方便运行使用 SQLite。真实项目可以保留表结构和页面查询逻辑，再把 `connect()` 替换成 PostgreSQL 连接，把 `seed_db()` 替换成真实 TSV / CSV / pipeline 结果导入逻辑。

## 8. 完整源码逐行注释

下面是项目三个核心 Python 文件的完整逐行注释版。代码列保留原始代码，注释列解释该行在当前模块中的作用。

### config.py 完整代码逐行注释

| 行号 | 代码 | 注释 |
|---:|---|---|
| 1 | `from pathlib import Path` | 从指定模块导入当前文件需要使用的类、函数或配置变量。 |
| 2 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 3 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 4 | `BASE_DIR = Path(__file__).resolve().parent` | 定义模块级常量，程序运行期间会被多个函数复用。 |
| 5 | `DATA_DIR = BASE_DIR / "data"` | 定义模块级常量，程序运行期间会被多个函数复用。 |
| 6 | `DATABASE_PATH = DATA_DIR / "znf_demo.sqlite3"` | 定义模块级常量，程序运行期间会被多个函数复用。 |
| 7 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 8 | `DEMO_DB = {` | 定义模块级常量，程序运行期间会被多个函数复用。 |
| 9 | `    "driver": "sqlite3",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 10 | `    "host": "localhost",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 11 | `    "port": "0",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 12 | `    "database": str(DATABASE_PATH),` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 13 | `    "user": "znf_demo_user",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 14 | `    "password": "znf_demo_pass_123",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 15 | `}` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 16 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 17 | `PROJECT_INFO = {` | 定义模块级常量，程序运行期间会被多个函数复用。 |
| 18 | `    "name": "HKZRSdb Demo",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 19 | `    "full_name": "Human KRAB-ZFPs &amp; Repetitive Sequences Database Demo",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 20 | `    "source_note": "教学复现版：使用本地 SQLite 与模拟数据，保留老师项目的数据结构和网页查询逻辑。",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 21 | `}` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 22 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |

### database.py 完整代码逐行注释

| 行号 | 代码 | 注释 |
|---:|---|---|
| 1 | `import json` | 导入 Python 标准库模块，供当前文件后续功能使用。 |
| 2 | `import sqlite3` | 导入 Python 标准库模块，供当前文件后续功能使用。 |
| 3 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 4 | `from config import DATABASE_PATH, DATA_DIR` | 从指定模块导入当前文件需要使用的类、函数或配置变量。 |
| 5 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 6 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 7 | `SCHEMA = """` | 定义模块级常量，程序运行期间会被多个函数复用。 |
| 8 | `CREATE TABLE IF NOT EXISTS znf (` | SQL 建表语句，定义一张数据库表。 |
| 9 | `    id INTEGER PRIMARY KEY AUTOINCREMENT,` | 主键字段，用来唯一标识表中的一条记录。 |
| 10 | `    ensembl TEXT UNIQUE,` | 唯一约束，保证该字段不会出现重复值。 |
| 11 | `    entrez_id TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 12 | `    gene_symbol TEXT UNIQUE NOT NULL,` | 唯一约束，保证该字段不会出现重复值。 |
| 13 | `    species TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 14 | `    family TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 15 | `    proteins TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 16 | `    gene_synonym TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 17 | `    uniprot_feature TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 18 | `    zinc_finger INTEGER` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 19 | `);` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 20 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 21 | `CREATE TABLE IF NOT EXISTS chip_data (` | SQL 建表语句，定义一张数据库表。 |
| 22 | `    id INTEGER PRIMARY KEY AUTOINCREMENT,` | 主键字段，用来唯一标识表中的一条记录。 |
| 23 | `    data_name TEXT UNIQUE NOT NULL,` | 唯一约束，保证该字段不会出现重复值。 |
| 24 | `    data_source TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 25 | `    repeat_number INTEGER,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 26 | `    peak_number INTEGER,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 27 | `    znf_gene_symbol TEXT NOT NULL,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 28 | `    FOREIGN KEY (znf_gene_symbol) REFERENCES znf(gene_symbol)` | 外键约束，表示当前字段关联另一张表的数据。 |
| 29 | `);` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 30 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 31 | `CREATE TABLE IF NOT EXISTS repeat (` | SQL 建表语句，定义一张数据库表。 |
| 32 | `    id INTEGER PRIMARY KEY AUTOINCREMENT,` | 主键字段，用来唯一标识表中的一条记录。 |
| 33 | `    repeat_name TEXT UNIQUE NOT NULL,` | 唯一约束，保证该字段不会出现重复值。 |
| 34 | `    sub_family TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 35 | `    main_family TEXT` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 36 | `);` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 37 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 38 | `CREATE TABLE IF NOT EXISTS peak (` | SQL 建表语句，定义一张数据库表。 |
| 39 | `    id INTEGER PRIMARY KEY AUTOINCREMENT,` | 主键字段，用来唯一标识表中的一条记录。 |
| 40 | `    chr TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 41 | `    start INTEGER,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 42 | `    end INTEGER,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 43 | `    strand TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 44 | `    enrichment REAL,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 45 | `    repeat_name TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 46 | `    znf_gene_symbol TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 47 | `    chip_data_name TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 48 | `    FOREIGN KEY (repeat_name) REFERENCES repeat(repeat_name),` | 外键约束，表示当前字段关联另一张表的数据。 |
| 49 | `    FOREIGN KEY (znf_gene_symbol) REFERENCES znf(gene_symbol),` | 外键约束，表示当前字段关联另一张表的数据。 |
| 50 | `    FOREIGN KEY (chip_data_name) REFERENCES chip_data(data_name)` | 外键约束，表示当前字段关联另一张表的数据。 |
| 51 | `);` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 52 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 53 | `CREATE TABLE IF NOT EXISTS repeat_region (` | SQL 建表语句，定义一张数据库表。 |
| 54 | `    id INTEGER PRIMARY KEY AUTOINCREMENT,` | 主键字段，用来唯一标识表中的一条记录。 |
| 55 | `    chr TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 56 | `    start INTEGER,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 57 | `    end INTEGER,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 58 | `    strand TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 59 | `    repeat_name TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 60 | `    znf_gene_symbol TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 61 | `    chip_data_name TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 62 | `    FOREIGN KEY (repeat_name) REFERENCES repeat(repeat_name),` | 外键约束，表示当前字段关联另一张表的数据。 |
| 63 | `    FOREIGN KEY (znf_gene_symbol) REFERENCES znf(gene_symbol),` | 外键约束，表示当前字段关联另一张表的数据。 |
| 64 | `    FOREIGN KEY (chip_data_name) REFERENCES chip_data(data_name)` | 外键约束，表示当前字段关联另一张表的数据。 |
| 65 | `);` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 66 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 67 | `CREATE TABLE IF NOT EXISTS motif (` | SQL 建表语句，定义一张数据库表。 |
| 68 | `    id INTEGER PRIMARY KEY AUTOINCREMENT,` | 主键字段，用来唯一标识表中的一条记录。 |
| 69 | `    chip_data_name TEXT UNIQUE,` | 唯一约束，保证该字段不会出现重复值。 |
| 70 | `    raw_motif TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 71 | `    full_motif TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 72 | `    part_motif TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 73 | `    none_motif TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 74 | `    FOREIGN KEY (chip_data_name) REFERENCES chip_data(data_name)` | 外键约束，表示当前字段关联另一张表的数据。 |
| 75 | `);` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 76 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 77 | `CREATE TABLE IF NOT EXISTS expression (` | SQL 建表语句，定义一张数据库表。 |
| 78 | `    id INTEGER PRIMARY KEY AUTOINCREMENT,` | 主键字段，用来唯一标识表中的一条记录。 |
| 79 | `    ensembl TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 80 | `    project TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 81 | `    cell_lines TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 82 | `    values_json TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 83 | `    FOREIGN KEY (ensembl) REFERENCES znf(ensembl)` | 外键约束，表示当前字段关联另一张表的数据。 |
| 84 | `);` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 85 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 86 | `CREATE TABLE IF NOT EXISTS gene_structure (` | SQL 建表语句，定义一张数据库表。 |
| 87 | `    id INTEGER PRIMARY KEY AUTOINCREMENT,` | 主键字段，用来唯一标识表中的一条记录。 |
| 88 | `    ensembl TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 89 | `    structure_json TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 90 | `    FOREIGN KEY (ensembl) REFERENCES znf(ensembl)` | 外键约束，表示当前字段关联另一张表的数据。 |
| 91 | `);` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 92 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 93 | `CREATE TABLE IF NOT EXISTS ortholog (` | SQL 建表语句，定义一张数据库表。 |
| 94 | `    id INTEGER PRIMARY KEY AUTOINCREMENT,` | 主键字段，用来唯一标识表中的一条记录。 |
| 95 | `    ensembl TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 96 | `    scientific_name TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 97 | `    ortholog_gene_name TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 98 | `    ortholog_id TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 99 | `    confidence TEXT,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 100 | `    FOREIGN KEY (ensembl) REFERENCES znf(ensembl)` | 外键约束，表示当前字段关联另一张表的数据。 |
| 101 | `);` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 102 | `"""` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 103 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 104 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 105 | `SAMPLE_ZNFS = [` | 定义模块级常量，程序运行期间会被多个函数复用。 |
| 106 | `    {` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 107 | `        "ensembl": "ENSG00000176171",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 108 | `        "entrez_id": "7739",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 109 | `        "gene_symbol": "ZNF197",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 110 | `        "species": "Homo_sapiens",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 111 | `        "family": "zf-C2H2",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 112 | `        "proteins": "Q9UK12",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 113 | `        "gene_synonym": "ZNF166; P18",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 114 | `        "uniprot_feature": [{"uniprot_id": "Q9UK12", "length": 1021, "zinc_finger": 12}],` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 115 | `        "zinc_finger": 12,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 116 | `    },` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 117 | `    {` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 118 | `        "ensembl": "ENSG00000198453",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 119 | `        "entrez_id": "7718",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 120 | `        "gene_symbol": "ZNF84",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 121 | `        "species": "Homo_sapiens",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 122 | `        "family": "zf-C2H2",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 123 | `        "proteins": "P51523",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 124 | `        "gene_synonym": "HPF2",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 125 | `        "uniprot_feature": [{"uniprot_id": "P51523", "length": 733, "zinc_finger": 10}],` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 126 | `        "zinc_finger": 10,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 127 | `    },` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 128 | `    {` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 129 | `        "ensembl": "ENSG00000197081",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 130 | `        "entrez_id": "7742",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 131 | `        "gene_symbol": "ZNF274",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 132 | `        "species": "Homo_sapiens",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 133 | `        "family": "zf-C2H2",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 134 | `        "proteins": "Q96GC6",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 135 | `        "gene_synonym": "ZKSCAN19",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 136 | `        "uniprot_feature": [{"uniprot_id": "Q96GC6", "length": 653, "zinc_finger": 5}],` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 137 | `        "zinc_finger": 5,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 138 | `    },` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 139 | `]` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 140 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 141 | `SAMPLE_CHIPS = [` | 定义模块级常量，程序运行期间会被多个函数复用。 |
| 142 | `    {"data_name": "GSM2466491", "data_source": "GSE78099", "znf_gene_symbol": "ZNF197"},` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 143 | `    {"data_name": "GSM2466677", "data_source": "GSE78099", "znf_gene_symbol": "ZNF84"},` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 144 | `    {"data_name": "GSM2466514", "data_source": "GSE78099", "znf_gene_symbol": "ZNF274"},` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 145 | `]` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 146 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 147 | `SAMPLE_REPEATS = [` | 定义模块级常量，程序运行期间会被多个函数复用。 |
| 148 | `    {"repeat_name": "L1PA7", "sub_family": "L1", "main_family": "LINE"},` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 149 | `    {"repeat_name": "AluY", "sub_family": "Alu", "main_family": "SINE"},` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 150 | `    {"repeat_name": "MER11A", "sub_family": "ERVK", "main_family": "LTR"},` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 151 | `    {"repeat_name": "SVA_D", "sub_family": "SVA", "main_family": "Retroposon"},` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 152 | `]` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 153 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 154 | `SAMPLE_PEAKS = [` | 定义模块级常量，程序运行期间会被多个函数复用。 |
| 155 | `    ("chr1", 120045, 120420, "+", 18.4, "L1PA7", "ZNF197", "GSM2466491"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 156 | `    ("chr1", 220010, 220388, "-", 12.1, "AluY", "ZNF197", "GSM2466491"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 157 | `    ("chr7", 991000, 991430, "+", 9.6, "MER11A", "ZNF197", "GSM2466491"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 158 | `    ("chr3", 510900, 511280, "+", 21.7, "AluY", "ZNF84", "GSM2466677"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 159 | `    ("chr5", 781400, 781850, "-", 15.2, "SVA_D", "ZNF84", "GSM2466677"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 160 | `    ("chr19", 338000, 338290, "+", 7.8, "L1PA7", "ZNF274", "GSM2466514"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 161 | `]` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 162 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 163 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 164 | `def connect():` | 定义函数，把一段可复用逻辑封装起来。 |
| 165 | `    DATA_DIR.mkdir(parents=True, exist_ok=True)` | 指定数据目录位置，数据库文件会放在这里。 |
| 166 | `    conn = sqlite3.connect(DATABASE_PATH)` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 167 | `    conn.row_factory = sqlite3.Row` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 168 | `    return conn` | 返回当前函数的处理结果。 |
| 169 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 170 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 171 | `def init_db():` | 定义函数，把一段可复用逻辑封装起来。 |
| 172 | `    with connect() as conn:` | 打开数据库连接，并在代码块结束时自动关闭或提交。 |
| 173 | `        conn.executescript(SCHEMA)` | 执行一条 SQL 语句，通常用于插入、查询或统计数据。 |
| 174 | `        seed_db(conn)` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 175 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 176 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 177 | `def seed_db(conn):` | 定义函数，把一段可复用逻辑封装起来。 |
| 178 | `    count = conn.execute("SELECT COUNT(*) AS n FROM znf").fetchone()["n"]` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 179 | `    if count:` | 条件判断，根据不同情况走不同分支。 |
| 180 | `        return` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 181 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 182 | `    for item in SAMPLE_ZNFS:` | 开始循环，逐个处理列表或查询结果中的元素。 |
| 183 | `        conn.execute(` | 执行一条 SQL 语句，通常用于插入、查询或统计数据。 |
| 184 | `            """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 185 | `            INSERT INTO znf` | SQL 插入语句，把模拟数据写入指定数据表。 |
| 186 | `            (ensembl, entrez_id, gene_symbol, species, family, proteins, gene_synonym, uniprot_feature, zinc_finger)` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 187 | `            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 188 | `            """,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 189 | `            (` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 190 | `                item["ensembl"],` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 191 | `                item["entrez_id"],` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 192 | `                item["gene_symbol"],` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 193 | `                item["species"],` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 194 | `                item["family"],` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 195 | `                item["proteins"],` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 196 | `                item["gene_synonym"],` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 197 | `                json.dumps(item["uniprot_feature"], ensure_ascii=False),` | 把 Python 对象转换成 JSON 字符串，方便保存或返回给前端。 |
| 198 | `                item["zinc_finger"],` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 199 | `            ),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 200 | `        )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 201 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 202 | `    for item in SAMPLE_REPEATS:` | 开始循环，逐个处理列表或查询结果中的元素。 |
| 203 | `        conn.execute(` | 执行一条 SQL 语句，通常用于插入、查询或统计数据。 |
| 204 | `            "INSERT INTO repeat (repeat_name, sub_family, main_family) VALUES (?, ?, ?)",` | SQL 插入语句，把模拟数据写入指定数据表。 |
| 205 | `            (item["repeat_name"], item["sub_family"], item["main_family"]),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 206 | `        )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 207 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 208 | `    for item in SAMPLE_CHIPS:` | 开始循环，逐个处理列表或查询结果中的元素。 |
| 209 | `        peak_count = sum(1 for peak in SAMPLE_PEAKS if peak[7] == item["data_name"])` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 210 | `        repeat_count = len({peak[5] for peak in SAMPLE_PEAKS if peak[7] == item["data_name"]})` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 211 | `        conn.execute(` | 执行一条 SQL 语句，通常用于插入、查询或统计数据。 |
| 212 | `            """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 213 | `            INSERT INTO chip_data (data_name, data_source, repeat_number, peak_number, znf_gene_symbol)` | SQL 插入语句，把模拟数据写入指定数据表。 |
| 214 | `            VALUES (?, ?, ?, ?, ?)` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 215 | `            """,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 216 | `            (item["data_name"], item["data_source"], repeat_count, peak_count, item["znf_gene_symbol"]),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 217 | `        )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 218 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 219 | `    for peak in SAMPLE_PEAKS:` | 开始循环，逐个处理列表或查询结果中的元素。 |
| 220 | `        conn.execute(` | 执行一条 SQL 语句，通常用于插入、查询或统计数据。 |
| 221 | `            """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 222 | `            INSERT INTO peak (chr, start, end, strand, enrichment, repeat_name, znf_gene_symbol, chip_data_name)` | SQL 插入语句，把模拟数据写入指定数据表。 |
| 223 | `            VALUES (?, ?, ?, ?, ?, ?, ?, ?)` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 224 | `            """,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 225 | `            peak,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 226 | `        )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 227 | `        conn.execute(` | 执行一条 SQL 语句，通常用于插入、查询或统计数据。 |
| 228 | `            """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 229 | `            INSERT INTO repeat_region (chr, start, end, strand, repeat_name, znf_gene_symbol, chip_data_name)` | SQL 插入语句，把模拟数据写入指定数据表。 |
| 230 | `            VALUES (?, ?, ?, ?, ?, ?, ?)` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 231 | `            """,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 232 | `            (peak[0], peak[1] + 30, peak[2] - 30, peak[3], peak[5], peak[6], peak[7]),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 233 | `        )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 234 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 235 | `    for chip in SAMPLE_CHIPS:` | 开始循环，逐个处理列表或查询结果中的元素。 |
| 236 | `        conn.execute(` | 执行一条 SQL 语句，通常用于插入、查询或统计数据。 |
| 237 | `            """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 238 | `            INSERT INTO motif (chip_data_name, raw_motif, full_motif, part_motif, none_motif)` | SQL 插入语句，把模拟数据写入指定数据表。 |
| 239 | `            VALUES (?, ?, ?, ?, ?)` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 240 | `            """,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 241 | `            (` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 242 | `                chip["data_name"],` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 243 | `                "A C T G G A",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 244 | `                "C C T G A A",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 245 | `                "A G G T C A",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 246 | `                "T T C A G G",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 247 | `            ),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 248 | `        )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 249 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 250 | `    for znf in SAMPLE_ZNFS:` | 开始循环，逐个处理列表或查询结果中的元素。 |
| 251 | `        conn.execute(` | 执行一条 SQL 语句，通常用于插入、查询或统计数据。 |
| 252 | `            """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 253 | `            INSERT INTO expression (ensembl, project, cell_lines, values_json)` | SQL 插入语句，把模拟数据写入指定数据表。 |
| 254 | `            VALUES (?, ?, ?, ?)` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 255 | `            """,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 256 | `            (` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 257 | `                znf["ensembl"],` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 258 | `                "E-MTAB-4748-demo",` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 259 | `                json.dumps(["K562", "HEK293", "HepG2"], ensure_ascii=False),` | 把 Python 对象转换成 JSON 字符串，方便保存或返回给前端。 |
| 260 | `                json.dumps([4.2, 7.8, 2.9]),` | 把 Python 对象转换成 JSON 字符串，方便保存或返回给前端。 |
| 261 | `            ),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 262 | `        )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 263 | `        conn.execute(` | 执行一条 SQL 语句，通常用于插入、查询或统计数据。 |
| 264 | `            """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 265 | `            INSERT INTO gene_structure (ensembl, structure_json)` | SQL 插入语句，把模拟数据写入指定数据表。 |
| 266 | `            VALUES (?, ?)` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 267 | `            """,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 268 | `            (` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 269 | `                znf["ensembl"],` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 270 | `                json.dumps(` | 把 Python 对象转换成 JSON 字符串，方便保存或返回给前端。 |
| 271 | `                    {` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 272 | `                        "gene_start": 100000,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 273 | `                        "gene_end": 126000,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 274 | `                        "exons": [` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 275 | `                            {"start": 100000, "end": 101200},` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 276 | `                            {"start": 108500, "end": 109300},` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 277 | `                            {"start": 124000, "end": 126000},` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 278 | `                        ],` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 279 | `                    },` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 280 | `                    ensure_ascii=False,` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 281 | `                ),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 282 | `            ),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 283 | `        )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 284 | `        conn.execute(` | 执行一条 SQL 语句，通常用于插入、查询或统计数据。 |
| 285 | `            """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 286 | `            INSERT INTO ortholog (ensembl, scientific_name, ortholog_gene_name, ortholog_id, confidence)` | SQL 插入语句，把模拟数据写入指定数据表。 |
| 287 | `            VALUES (?, ?, ?, ?, ?)` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 288 | `            """,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 289 | `            (znf["ensembl"], "Mus musculus", znf["gene_symbol"].title(), "ENSMUSG-demo", "high"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 290 | `        )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 291 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 292 | `    conn.commit()` | 提交本次事务，把插入的数据真正写入数据库。 |
| 293 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 294 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 295 | `def rows(query, params=()):` | 定义函数，把一段可复用逻辑封装起来。 |
| 296 | `    with connect() as conn:` | 打开数据库连接，并在代码块结束时自动关闭或提交。 |
| 297 | `        return [dict(row) for row in conn.execute(query, params).fetchall()]` | 返回当前函数的处理结果。 |
| 298 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 299 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 300 | `def row(query, params=()):` | 定义函数，把一段可复用逻辑封装起来。 |
| 301 | `    with connect() as conn:` | 打开数据库连接，并在代码块结束时自动关闭或提交。 |
| 302 | `        item = conn.execute(query, params).fetchone()` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 303 | `        return dict(item) if item else None` | 返回当前函数的处理结果。 |
| 304 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |

### app.py 完整代码逐行注释

| 行号 | 代码 | 注释 |
|---:|---|---|
| 1 | `import html` | 导入 Python 标准库模块，供当前文件后续功能使用。 |
| 2 | `import json` | 导入 Python 标准库模块，供当前文件后续功能使用。 |
| 3 | `from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer` | 从指定模块导入当前文件需要使用的类、函数或配置变量。 |
| 4 | `from urllib.parse import parse_qs, quote, unquote, urlparse` | 从指定模块导入当前文件需要使用的类、函数或配置变量。 |
| 5 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 6 | `from config import DEMO_DB, PROJECT_INFO` | 从指定模块导入当前文件需要使用的类、函数或配置变量。 |
| 7 | `from database import init_db, row, rows` | 从指定模块导入当前文件需要使用的类、函数或配置变量。 |
| 8 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 9 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 10 | `HOST = "127.0.0.1"` | 定义模块级常量，程序运行期间会被多个函数复用。 |
| 11 | `PORT = 5050` | 定义模块级常量，程序运行期间会被多个函数复用。 |
| 12 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 13 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 14 | `def page(title, body):` | 定义函数，把一段可复用逻辑封装起来。 |
| 15 | `    return f"""&lt;!doctype html&gt;` | 返回当前函数的处理结果。 |
| 16 | `&lt;html lang="zh"&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 17 | `&lt;head&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 18 | `  &lt;meta charset="utf-8"&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 19 | `  &lt;meta name="viewport" content="width=device-width, initial-scale=1"&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 20 | `  &lt;title&gt;{html.escape(title)}&lt;/title&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 21 | `  &lt;style&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 22 | `    :root {{ color-scheme: light; --ink:#1f2937; --muted:#64748b; --line:#d8dee9; --brand:#0f766e; --soft:#f1f5f9; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 23 | `    body {{ margin:0; font-family: Arial, "PingFang SC", "Microsoft YaHei", sans-serif; color:var(--ink); background:#fbfdff; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 24 | `    header {{ background:#102a43; color:white; padding:18px 0; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 25 | `    main, .nav-inner {{ width:min(1100px, calc(100% - 32px)); margin:auto; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 26 | `    nav {{ display:flex; align-items:center; justify-content:space-between; gap:18px; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 27 | `    nav a {{ color:white; text-decoration:none; margin-left:18px; font-weight:600; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 28 | `    h1 {{ margin:28px 0 12px; font-size:30px; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 29 | `    h2 {{ margin:28px 0 10px; font-size:22px; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 30 | `    p {{ line-height:1.75; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 31 | `    .muted {{ color:var(--muted); }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 32 | `    .grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:14px; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 33 | `    .card {{ background:white; border:1px solid var(--line); border-radius:8px; padding:16px; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 34 | `    .metric {{ font-size:28px; font-weight:700; color:var(--brand); }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 35 | `    table {{ width:100%; border-collapse:collapse; background:white; border:1px solid var(--line); }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 36 | `    th, td {{ padding:10px 12px; border-bottom:1px solid var(--line); text-align:left; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 37 | `    th {{ background:var(--soft); }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 38 | `    input {{ padding:10px 12px; border:1px solid var(--line); border-radius:6px; min-width:260px; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 39 | `    button, .button {{ padding:10px 14px; border:0; border-radius:6px; background:var(--brand); color:white; text-decoration:none; cursor:pointer; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 40 | `    code {{ background:var(--soft); padding:2px 5px; border-radius:4px; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 41 | `    .bar {{ height:12px; background:#dbeafe; border-radius:20px; overflow:hidden; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 42 | `    .bar span {{ display:block; height:100%; background:#0f766e; }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 43 | `    footer {{ margin-top:40px; padding:20px 0; border-top:1px solid var(--line); color:var(--muted); }}` | CSS 或 HTML 模板样式，控制页面布局、颜色和间距。 |
| 44 | `  &lt;/style&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 45 | `&lt;/head&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 46 | `&lt;body&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 47 | `  &lt;header&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 48 | `    &lt;div class="nav-inner"&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 49 | `      &lt;nav&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 50 | `        &lt;strong&gt;{html.escape(PROJECT_INFO["name"])}&lt;/strong&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 51 | `        &lt;div&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 52 | `          &lt;a href="/"&gt;首页&lt;/a&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 53 | `          &lt;a href="/kzfp"&gt;KZFP&lt;/a&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 54 | `          &lt;a href="/repeat"&gt;Repeat&lt;/a&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 55 | `          &lt;a href="/about"&gt;配置说明&lt;/a&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 56 | `        &lt;/div&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 57 | `      &lt;/nav&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 58 | `    &lt;/div&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 59 | `  &lt;/header&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 60 | `  &lt;main&gt;{body}&lt;/main&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 61 | `  &lt;footer&gt;&lt;main&gt;本地教学复现版，默认使用 SQLite 模拟数据库。&lt;/main&gt;&lt;/footer&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 62 | `&lt;/body&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 63 | `&lt;/html&gt;"""` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 64 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 65 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 66 | `def table(items, columns):` | 定义函数，把一段可复用逻辑封装起来。 |
| 67 | `    if not items:` | 条件判断，根据不同情况走不同分支。 |
| 68 | `        return "&lt;p class='muted'&gt;暂无数据。&lt;/p&gt;"` | 返回当前函数的处理结果。 |
| 69 | `    head = "".join(f"&lt;th&gt;{html.escape(label)}&lt;/th&gt;" for _, label in columns)` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 70 | `    body = []` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 71 | `    for item in items:` | 开始循环，逐个处理列表或查询结果中的元素。 |
| 72 | `        cells = []` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 73 | `        for key, _ in columns:` | 开始循环，逐个处理列表或查询结果中的元素。 |
| 74 | `            value = item.get(key, "")` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 75 | `            cells.append(f"&lt;td&gt;{value}&lt;/td&gt;")` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 76 | `        body.append("&lt;tr&gt;" + "".join(cells) + "&lt;/tr&gt;")` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 77 | `    return "&lt;table&gt;&lt;thead&gt;&lt;tr&gt;" + head + "&lt;/tr&gt;&lt;/thead&gt;&lt;tbody&gt;" + "".join(body) + "&lt;/tbody&gt;&lt;/table&gt;"` | 返回当前函数的处理结果。 |
| 78 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 79 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 80 | `def home():` | 定义函数，把一段可复用逻辑封装起来。 |
| 81 | `    znf_count = row("SELECT COUNT(*) AS n FROM znf")["n"]` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 82 | `    peak_count = row("SELECT COUNT(*) AS n FROM peak")["n"]` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 83 | `    repeat_count = row("SELECT COUNT(*) AS n FROM repeat")["n"]` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 84 | `    chip_count = row("SELECT COUNT(*) AS n FROM chip_data")["n"]` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 85 | `    body = f"""` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 86 | `      &lt;h1&gt;{html.escape(PROJECT_INFO["full_name"])}&lt;/h1&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 87 | `      &lt;p class="muted"&gt;{html.escape(PROJECT_INFO["source_note"])}&lt;/p&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 88 | `      &lt;section class="grid"&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 89 | `        &lt;div class="card"&gt;&lt;div class="metric"&gt;{znf_count}&lt;/div&gt;&lt;div&gt;ZNF genes&lt;/div&gt;&lt;/div&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 90 | `        &lt;div class="card"&gt;&lt;div class="metric"&gt;{chip_count}&lt;/div&gt;&lt;div&gt;ChIP-seq datasets&lt;/div&gt;&lt;/div&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 91 | `        &lt;div class="card"&gt;&lt;div class="metric"&gt;{peak_count}&lt;/div&gt;&lt;div&gt;Peak records&lt;/div&gt;&lt;/div&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 92 | `        &lt;div class="card"&gt;&lt;div class="metric"&gt;{repeat_count}&lt;/div&gt;&lt;div&gt;Repeat classes&lt;/div&gt;&lt;/div&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 93 | `      &lt;/section&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 94 | `      &lt;h2&gt;搜索 ZNF&lt;/h2&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 95 | `      &lt;form action="/search_znf" method="get"&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 96 | `        &lt;input name="q" placeholder="输入 ZNF197、ZNF84 或 ZNF274"&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 97 | `        &lt;button type="submit"&gt;搜索&lt;/button&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 98 | `      &lt;/form&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 99 | `      &lt;h2&gt;复现目标&lt;/h2&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 100 | `      &lt;p&gt;这个版本用模拟数据跑通完整闭环：ZNF 基础信息、ChIP-seq 数据、peak、repeat、motif、表达量、基因结构和 orthologs。后续只要把 &lt;code&gt;database.py&lt;/code&gt; 中的模拟数据替换为真实导入脚本，就能对接老师项目的数据处理流程。&lt;/p&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 101 | `    """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 102 | `    return page("首页", body)` | 返回当前函数的处理结果。 |
| 103 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 104 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 105 | `def kzfp():` | 定义函数，把一段可复用逻辑封装起来。 |
| 106 | `    items = rows(` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 107 | `        """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 108 | `        SELECT z.gene_symbol, z.ensembl, z.family, c.data_name, c.data_source, c.peak_number, c.repeat_number` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 109 | `        FROM znf z` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 110 | `        LEFT JOIN chip_data c ON c.znf_gene_symbol = z.gene_symbol` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 111 | `        ORDER BY z.gene_symbol` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 112 | `        """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 113 | `    )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 114 | `    for item in items:` | 开始循环，逐个处理列表或查询结果中的元素。 |
| 115 | `        symbol = quote(item["gene_symbol"])` | 对 URL 参数进行编码，保证链接里的特殊字符安全。 |
| 116 | `        item["gene_symbol"] = f'&lt;a href="/znf?symbol={symbol}"&gt;{html.escape(item["gene_symbol"])}&lt;/a&gt;'` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 117 | `    body = "&lt;h1&gt;KZFP / ZNF 总览&lt;/h1&gt;" + table(` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 118 | `        items,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 119 | `        [` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 120 | `            ("gene_symbol", "ZNF"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 121 | `            ("ensembl", "Ensembl"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 122 | `            ("family", "Family"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 123 | `            ("data_name", "Data No."),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 124 | `            ("data_source", "Source"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 125 | `            ("peak_number", "Peaks"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 126 | `            ("repeat_number", "Repeats"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 127 | `        ],` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 128 | `    )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 129 | `    return page("KZFP", body)` | 返回当前函数的处理结果。 |
| 130 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 131 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 132 | `def repeat_page():` | 定义函数，把一段可复用逻辑封装起来。 |
| 133 | `    items = rows(` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 134 | `        """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 135 | `        SELECT r.id, r.repeat_name, r.sub_family, r.main_family,` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 136 | `               COUNT(DISTINCT p.znf_gene_symbol) AS znf_number,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 137 | `               COUNT(p.id) AS peak_number` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 138 | `        FROM repeat r` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 139 | `        LEFT JOIN peak p ON p.repeat_name = r.repeat_name` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 140 | `        GROUP BY r.id` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 141 | `        ORDER BY r.repeat_name` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 142 | `        """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 143 | `    )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 144 | `    for item in items:` | 开始循环，逐个处理列表或查询结果中的元素。 |
| 145 | `        item["repeat_name"] = f'&lt;a href="/repeat_one?id={item["id"]}"&gt;{html.escape(item["repeat_name"])}&lt;/a&gt;'` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 146 | `    body = "&lt;h1&gt;Repeat 总览&lt;/h1&gt;" + table(` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 147 | `        items,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 148 | `        [` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 149 | `            ("repeat_name", "Repeat"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 150 | `            ("sub_family", "Sub family"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 151 | `            ("main_family", "Main family"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 152 | `            ("znf_number", "Related ZNF"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 153 | `            ("peak_number", "Overlapped peaks"),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 154 | `        ],` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 155 | `    )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 156 | `    return page("Repeat", body)` | 返回当前函数的处理结果。 |
| 157 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 158 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 159 | `def znf_detail(symbol):` | 定义函数，把一段可复用逻辑封装起来。 |
| 160 | `    item = row("SELECT * FROM znf WHERE gene_symbol = ?", (symbol,))` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 161 | `    if not item:` | 条件判断，根据不同情况走不同分支。 |
| 162 | `        return page("未找到", "&lt;h1&gt;没有找到这个 ZNF&lt;/h1&gt;&lt;p&gt;&lt;a href='/kzfp'&gt;返回 KZFP 列表&lt;/a&gt;&lt;/p&gt;")` | 返回当前函数的处理结果。 |
| 163 | `    chip = row("SELECT * FROM chip_data WHERE znf_gene_symbol = ?", (symbol,))` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 164 | `    peaks = rows("SELECT * FROM peak WHERE znf_gene_symbol = ? ORDER BY enrichment DESC", (symbol,))` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 165 | `    expression = row("SELECT * FROM expression WHERE ensembl = ?", (item["ensembl"],))` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 166 | `    structure = row("SELECT * FROM gene_structure WHERE ensembl = ?", (item["ensembl"],))` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 167 | `    orthologs = rows("SELECT * FROM ortholog WHERE ensembl = ?", (item["ensembl"],))` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 168 | `    repeat_counts = rows(` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 169 | `        """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 170 | `        SELECT repeat_name, COUNT(*) AS n` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 171 | `        FROM peak` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 172 | `        WHERE znf_gene_symbol = ?` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 173 | `        GROUP BY repeat_name` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 174 | `        ORDER BY n DESC` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 175 | `        """,` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 176 | `        (symbol,),` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 177 | `    )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 178 | `    bars = "".join(` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 179 | `        f"&lt;p&gt;{html.escape(r['repeat_name'])}: {r['n']}&lt;/p&gt;&lt;div class='bar'&gt;&lt;span style='width:{min(r['n'] * 35, 100)}%'&gt;&lt;/span&gt;&lt;/div&gt;"` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 180 | `        for r in repeat_counts` | 开始循环，逐个处理列表或查询结果中的元素。 |
| 181 | `    )` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 182 | `    expr = ""` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 183 | `    if expression:` | 条件判断，根据不同情况走不同分支。 |
| 184 | `        cells = json.loads(expression["cell_lines"])` | 把数据库中的 JSON 字符串解析回 Python 对象。 |
| 185 | `        values = json.loads(expression["values_json"])` | 把数据库中的 JSON 字符串解析回 Python 对象。 |
| 186 | `        expr = table([{"cell": c, "value": v} for c, v in zip(cells, values)], [("cell", "Cell line"), ("value", "TPM demo")])` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 187 | `    gene = ""` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 188 | `    if structure:` | 条件判断，根据不同情况走不同分支。 |
| 189 | `        gene = f"&lt;pre&gt;{html.escape(json.dumps(json.loads(structure['structure_json']), ensure_ascii=False, indent=2))}&lt;/pre&gt;"` | 把 Python 对象转换成 JSON 字符串，方便保存或返回给前端。 |
| 190 | `    body = f"""` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 191 | `      &lt;h1&gt;{html.escape(item["gene_symbol"])} 详情&lt;/h1&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 192 | `      &lt;section class="grid"&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 193 | `        &lt;div class="card"&gt;&lt;strong&gt;Ensembl&lt;/strong&gt;&lt;p&gt;{html.escape(item["ensembl"])}&lt;/p&gt;&lt;/div&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 194 | `        &lt;div class="card"&gt;&lt;strong&gt;Entrez ID&lt;/strong&gt;&lt;p&gt;{html.escape(item["entrez_id"])}&lt;/p&gt;&lt;/div&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 195 | `        &lt;div class="card"&gt;&lt;strong&gt;Zinc fingers&lt;/strong&gt;&lt;p&gt;{item["zinc_finger"]}&lt;/p&gt;&lt;/div&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 196 | `        &lt;div class="card"&gt;&lt;strong&gt;Dataset&lt;/strong&gt;&lt;p&gt;{html.escape(chip["data_name"]) if chip else ""}&lt;/p&gt;&lt;/div&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 197 | `      &lt;/section&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 198 | `      &lt;h2&gt;Repeat overlap 分布&lt;/h2&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 199 | `      {bars or "&lt;p class='muted'&gt;暂无 repeat overlap。&lt;/p&gt;"}` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 200 | `      &lt;h2&gt;Peaks&lt;/h2&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 201 | `      {table(peaks, [("chr", "Chr"), ("start", "Start"), ("end", "End"), ("strand", "Strand"), ("enrichment", "Enrichment"), ("repeat_name", "Repeat")])}` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 202 | `      &lt;h2&gt;Expression&lt;/h2&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 203 | `      {expr}` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 204 | `      &lt;h2&gt;Gene structure JSON&lt;/h2&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 205 | `      {gene}` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 206 | `      &lt;h2&gt;Orthologs&lt;/h2&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 207 | `      {table(orthologs, [("scientific_name", "Species"), ("ortholog_gene_name", "Gene"), ("ortholog_id", "Ortholog ID"), ("confidence", "Confidence")])}` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 208 | `    """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 209 | `    return page(item["gene_symbol"], body)` | 返回当前函数的处理结果。 |
| 210 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 211 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 212 | `def repeat_detail(repeat_id):` | 定义函数，把一段可复用逻辑封装起来。 |
| 213 | `    item = row("SELECT * FROM repeat WHERE id = ?", (repeat_id,))` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 214 | `    if not item:` | 条件判断，根据不同情况走不同分支。 |
| 215 | `        return page("未找到", "&lt;h1&gt;没有找到这个 repeat&lt;/h1&gt;&lt;p&gt;&lt;a href='/repeat'&gt;返回 Repeat 列表&lt;/a&gt;&lt;/p&gt;")` | 返回当前函数的处理结果。 |
| 216 | `    regions = rows("SELECT * FROM repeat_region WHERE repeat_name = ? ORDER BY chr, start", (item["repeat_name"],))` | SQL 查询语句，从数据库表中取出页面需要的数据。 |
| 217 | `    body = f"""` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 218 | `      &lt;h1&gt;{html.escape(item["repeat_name"])} 详情&lt;/h1&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 219 | `      &lt;section class="grid"&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 220 | `        &lt;div class="card"&gt;&lt;strong&gt;Sub family&lt;/strong&gt;&lt;p&gt;{html.escape(item["sub_family"])}&lt;/p&gt;&lt;/div&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 221 | `        &lt;div class="card"&gt;&lt;strong&gt;Main family&lt;/strong&gt;&lt;p&gt;{html.escape(item["main_family"])}&lt;/p&gt;&lt;/div&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 222 | `        &lt;div class="card"&gt;&lt;strong&gt;Region count&lt;/strong&gt;&lt;p&gt;{len(regions)}&lt;/p&gt;&lt;/div&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 223 | `      &lt;/section&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 224 | `      &lt;h2&gt;Repeat regions&lt;/h2&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 225 | `      {table(regions, [("chr", "Chr"), ("start", "Start"), ("end", "End"), ("strand", "Strand"), ("znf_gene_symbol", "ZNF"), ("chip_data_name", "Dataset")])}` | 结构性符号，负责结束或连接上面的数据结构、函数调用或 SQL 参数。 |
| 226 | `    """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 227 | `    return page(item["repeat_name"], body)` | 返回当前函数的处理结果。 |
| 228 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 229 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 230 | `def about():` | 定义函数，把一段可复用逻辑封装起来。 |
| 231 | `    body = f"""` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 232 | `      &lt;h1&gt;配置说明&lt;/h1&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 233 | `      &lt;p&gt;这个版本已经把原项目中的路径、账号和密码全部改成可迁移配置。&lt;/p&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 234 | `      &lt;table&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 235 | `        &lt;tr&gt;&lt;th&gt;配置项&lt;/th&gt;&lt;th&gt;当前模拟值&lt;/th&gt;&lt;/tr&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 236 | `        &lt;tr&gt;&lt;td&gt;driver&lt;/td&gt;&lt;td&gt;{html.escape(DEMO_DB["driver"])}&lt;/td&gt;&lt;/tr&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 237 | `        &lt;tr&gt;&lt;td&gt;host&lt;/td&gt;&lt;td&gt;{html.escape(DEMO_DB["host"])}&lt;/td&gt;&lt;/tr&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 238 | `        &lt;tr&gt;&lt;td&gt;database&lt;/td&gt;&lt;td&gt;{html.escape(DEMO_DB["database"])}&lt;/td&gt;&lt;/tr&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 239 | `        &lt;tr&gt;&lt;td&gt;user&lt;/td&gt;&lt;td&gt;{html.escape(DEMO_DB["user"])}&lt;/td&gt;&lt;/tr&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 240 | `        &lt;tr&gt;&lt;td&gt;password&lt;/td&gt;&lt;td&gt;{html.escape(DEMO_DB["password"])}&lt;/td&gt;&lt;/tr&gt;` | 对页面文本做 HTML 转义，避免特殊字符破坏页面结构。 |
| 241 | `      &lt;/table&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 242 | `      &lt;h2&gt;切换到真实 PostgreSQL 的思路&lt;/h2&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 243 | `      &lt;p&gt;教学版默认用 SQLite，方便直接运行。等你要接真实数据时，可以用 Flask + SQLAlchemy 版本，把数据库连接改成类似 &lt;code&gt;postgresql://znf_demo_user:znf_demo_pass_123@localhost:5432/znf_demo_db&lt;/code&gt;，同时把 &lt;code&gt;data/&lt;/code&gt; 下的模拟数据替换成老师项目的 GSE78099、UniProt、expression、gene structure 数据。&lt;/p&gt;` | HTML 模板内容，最终会被浏览器渲染成页面。 |
| 244 | `    """` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 245 | `    return page("配置说明", body)` | 返回当前函数的处理结果。 |
| 246 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 247 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 248 | `def api(path):` | 定义函数，把一段可复用逻辑封装起来。 |
| 249 | `    if path == "/api/znfs":` | 条件判断，根据不同情况走不同分支。 |
| 250 | `        return rows("SELECT * FROM znf ORDER BY gene_symbol")` | 返回当前函数的处理结果。 |
| 251 | `    if path == "/api/repeats":` | 条件判断，根据不同情况走不同分支。 |
| 252 | `        return rows("SELECT * FROM repeat ORDER BY repeat_name")` | 返回当前函数的处理结果。 |
| 253 | `    if path == "/api/peaks":` | 条件判断，根据不同情况走不同分支。 |
| 254 | `        return rows("SELECT * FROM peak ORDER BY id")` | 返回当前函数的处理结果。 |
| 255 | `    return {"error": "unknown api"}` | 返回当前函数的处理结果。 |
| 256 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 257 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 258 | `class Handler(BaseHTTPRequestHandler):` | 定义请求处理类，用来接收浏览器请求并返回响应。 |
| 259 | `    def do_GET(self):` | 定义函数，把一段可复用逻辑封装起来。 |
| 260 | `        parsed = urlparse(self.path)` | 解析浏览器请求 URL，拆出路径和查询字符串。 |
| 261 | `        path = parsed.path` | 取得 URL 路径部分，用来判断用户访问哪个页面。 |
| 262 | `        params = parse_qs(parsed.query)` | 解析 URL 查询参数，例如 symbol=ZNF197。 |
| 263 | `        if path.startswith("/api/"):` | 条件判断，根据不同情况走不同分支。 |
| 264 | `            self.send_json(api(path))` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 265 | `            return` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 266 | `        if path == "/":` | 条件判断，根据不同情况走不同分支。 |
| 267 | `            self.send_html(home())` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 268 | `            return` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 269 | `        if path == "/kzfp":` | 条件判断，根据不同情况走不同分支。 |
| 270 | `            self.send_html(kzfp())` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 271 | `            return` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 272 | `        if path == "/repeat":` | 条件判断，根据不同情况走不同分支。 |
| 273 | `            self.send_html(repeat_page())` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 274 | `            return` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 275 | `        if path == "/znf":` | 条件判断，根据不同情况走不同分支。 |
| 276 | `            self.send_html(znf_detail(unquote(params.get("symbol", [""])[0])))` | 对 URL 参数进行编码，保证链接里的特殊字符安全。 |
| 277 | `            return` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 278 | `        if path == "/repeat_one":` | 条件判断，根据不同情况走不同分支。 |
| 279 | `            self.send_html(repeat_detail(params.get("id", ["0"])[0]))` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 280 | `            return` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 281 | `        if path == "/search_znf":` | 条件判断，根据不同情况走不同分支。 |
| 282 | `            self.send_html(znf_detail(unquote(params.get("q", [""])[0].strip())))` | 对 URL 参数进行编码，保证链接里的特殊字符安全。 |
| 283 | `            return` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 284 | `        if path == "/about":` | 条件判断，根据不同情况走不同分支。 |
| 285 | `            self.send_html(about())` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 286 | `            return` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 287 | `        self.send_html(page("404", "&lt;h1&gt;404&lt;/h1&gt;&lt;p&gt;页面不存在。&lt;/p&gt;"), 404)` | 拼接 HTML 片段，用来组成最终返回给浏览器的页面。 |
| 288 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 289 | `    def send_html(self, content, status=200):` | 定义函数，把一段可复用逻辑封装起来。 |
| 290 | `        data = content.encode("utf-8")` | 给变量赋值，保存后续逻辑需要使用的中间结果。 |
| 291 | `        self.send_response(status)` | 设置 HTTP 状态码，例如 200 或 404。 |
| 292 | `        self.send_header("Content-Type", "text/html; charset=utf-8")` | 设置 HTTP 响应头，告诉浏览器内容类型和长度。 |
| 293 | `        self.send_header("Content-Length", str(len(data)))` | 设置 HTTP 响应头，告诉浏览器内容类型和长度。 |
| 294 | `        self.end_headers()` | 结束响应头部分，准备写入响应正文。 |
| 295 | `        self.wfile.write(data)` | 把编码后的 HTML 或 JSON 内容写回浏览器。 |
| 296 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 297 | `    def send_json(self, content, status=200):` | 定义函数，把一段可复用逻辑封装起来。 |
| 298 | `        data = json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8")` | 把 Python 对象转换成 JSON 字符串，方便保存或返回给前端。 |
| 299 | `        self.send_response(status)` | 设置 HTTP 状态码，例如 200 或 404。 |
| 300 | `        self.send_header("Content-Type", "application/json; charset=utf-8")` | 设置 HTTP 响应头，告诉浏览器内容类型和长度。 |
| 301 | `        self.send_header("Content-Length", str(len(data)))` | 设置 HTTP 响应头，告诉浏览器内容类型和长度。 |
| 302 | `        self.end_headers()` | 结束响应头部分，准备写入响应正文。 |
| 303 | `        self.wfile.write(data)` | 把编码后的 HTML 或 JSON 内容写回浏览器。 |
| 304 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 305 | `    def log_message(self, fmt, *args):` | 定义函数，把一段可复用逻辑封装起来。 |
| 306 | `        print("%s - %s" % (self.address_string(), fmt % args))` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 307 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 308 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 309 | `def main():` | 定义函数，把一段可复用逻辑封装起来。 |
| 310 | `    init_db()` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 311 | `    server = ThreadingHTTPServer((HOST, PORT), Handler)` | 创建多线程 HTTP 服务，让浏览器可以访问本地页面。 |
| 312 | `    print(f"HKZRSdb demo is running at http://{HOST}:{PORT}")` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 313 | `    print("Press Ctrl+C to stop.")` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 314 | `    server.serve_forever()` | 启动服务循环，让程序持续监听浏览器请求。 |
| 315 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 316 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |
| 317 | `if __name__ == "__main__":` | 条件判断，根据不同情况走不同分支。 |
| 318 | `    main()` | 当前行属于所在代码块的一部分，配合上下文完成模块功能。 |
| 319 | `` | 空行，用来分隔不同逻辑块，让代码结构更清楚。 |

## 9. 学习顺序建议

1. 先读 `config.py`，理解路径和配置从哪里来。
2. 再读 `database.py` 的 `SCHEMA`，理解数据库有哪些表。
3. 继续读 `seed_db()`，理解模拟数据如何进入数据库。
4. 最后读 `app.py` 的 `Handler.do_GET()`，把 URL 和页面函数对应起来。
5. 修改一条模拟数据，删除数据库文件，重新运行，观察页面变化。

## 10. 运行验证命令

```bash
cd /Users/chengyuhang2/Desktop/runnable_znf_db
python3 -m py_compile app.py database.py config.py
python3 app.py
```

`py_compile` 没有输出就代表 Python 语法检查通过。
