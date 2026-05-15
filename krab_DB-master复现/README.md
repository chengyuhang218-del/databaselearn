# KRAB DB 项目复现说明

这是一个基于 Flask + SQLAlchemy + PostgreSQL 的 KRAB/ZNF 数据库网站项目。老师原始文件夹没有提供完整原始数据集，因此本整理版额外加入了一个很小的演示数据脚本 `seed_demo_data.py`，用于在没有真实数据时把页面跑通。

数据库账号统一为：

- 用户：`cyh666`
- 密码：`666666`
- 数据库：`ZNFdb`

## 1. 项目结构

```text
krab_DB-master/
  app.py              Flask 应用入口，补齐老师代码中 from app import app 的依赖
  routes.py           Web 页面路由、搜索接口、JSON API
  ZFWebDatabase.py    SQLAlchemy ORM 表结构和数据库操作封装
  import_data.py      老师原始完整数据导入脚本，依赖外部生信数据文件
  seed_demo_data.py   本地演示数据生成脚本，无真实数据集时用于跑通页面
  requirements.txt    Python 依赖
  templates/          Jinja2 HTML 页面模板
  static/             CSS/JS/图片和 summary 静态文件
  database/           旧版/备份数据库建表和导入脚本
```

更详细的模块说明见 `MODULES.md`。

## 2. 环境准备

建议 Python 版本使用 3.8-3.10。项目原代码较旧，完整跑 `import_data.py` 时可能会遇到 pandas 旧接口问题，例如 `.ix`，后续可按报错改成 `.loc` 或 `.iloc`。

```powershell
cd C:\Users\cheng\Documents\Codex\2026-05-14\c-users-cheng-desktop-krab-db\krab_DB-master
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. PostgreSQL 数据库准备

安装 PostgreSQL 后创建用户和数据库：

```sql
CREATE USER cyh666 WITH PASSWORD '666666';
CREATE DATABASE "ZNFdb" OWNER cyh666;
GRANT ALL PRIVILEGES ON DATABASE "ZNFdb" TO cyh666;
```

默认连接信息仍沿用老师源代码中的直接写法，只把账号密码替换为 `cyh666/666666`。

## 4. 建表

只创建空表：

```powershell
python ZFWebDatabase.py
```

这会调用 `Base.metadata.create_all()`，创建 `znf`、`chip_data`、`repeat`、`peaks`、`expression`、`gene_structure`、`orthologs` 等表。

## 5. 没有真实数据集时：导入演示数据

如果只是学习代码结构、验证网站能打开，可以直接导入演示数据：

```powershell
python seed_demo_data.py
```

脚本会插入一组最小闭环数据：

- 1 个 ZNF：`ZNFDEMO1`
- 1 个 Repeat：`DEMO_REPEAT_A`
- 1 个 ChIP 数据集：`GSMDEMO001`
- 3 条 peak 和 repeat region
- 1 组 expression / cell line / gene structure / orthologs 数据
- 4 组 motif 占位图片和 matrix 文件

重复运行时，如果演示数据已存在，脚本会跳过。需要重建演示数据时使用：

```powershell
python seed_demo_data.py --refresh-demo
```

启动网站后可以测试：

- ZNF 搜索：`ZNFDEMO1`
- Repeat 搜索：`DEMO_REPEAT_A`
- 详情页：`/KZFP/zinc_fingure/GSMDEMO001`

## 6. 有老师真实数据时：完整导入

完整导入入口仍是老师原来的脚本：

```powershell
python import_data.py
```

注意：`import_data.py` 中的数据路径仍指向老师 Linux 机器上的路径，例如：

```text
/home/luozhihui/PycharmProjects/ZNFdatabase/data/GSE78099_diff/diff
/home/luozhihui/Project/ZF_database/data_process/C2H2_list/
/home/luozhihui/Project/ZF_database/data_process/expression/cell_line
```

要完整复现真实数据库，需要先拿到这些原始数据文件，再把脚本中的路径改成本机路径。导入顺序在脚本底部：

1. `C2H2_information()`
2. `import_basic_information()`
3. `import_repeat()`
4. `import_peaks()`
5. `import_expression()`
6. `import_gene_structure()`
7. `import_orthologs()`

## 7. 启动网站

数据库中有数据后启动 Flask：

```powershell
flask --app app run --host 127.0.0.1 --port 5000
```

访问：

```text
http://127.0.0.1:5000/
```

主要页面：

- `/` 或 `/index/`：首页
- `/KZFP/`：ZNF/KZFP 检索
- `/Repeat/`：Repeat 检索
- `/Expression/`：表达页面
- `/Help/`：帮助页面
- `/About/`：关于页面

## 8. 当前整理版只做了这些必要补充

- 补齐 `app.py`，使 `routes.py` 中的 `from app import app` 可以正常工作。
- 新增 `requirements.txt`。
- 新增 `seed_demo_data.py`，用于没有真实数据时生成演示数据。
- 将数据库账号密码从 `luozh/luozh123` 改为 `cyh666/666666`。
- 修正 ZNF 搜索跳转参数，使表单搜索到基因后进入该基因的第一个 ChIP 数据详情。
- 修正 Repeat 搜索字段，从错误的 `gene_symbol` 改为 `repeat_name`。
- 修正两个列表页本地链接，避免使用行号或外网 IP 导致本地详情页打不开。
- 修正详情页 orthologs 查询参数，使用当前 ZNF 的 Ensembl ID。

## 9. 仍需注意

- 演示数据只用于跑通代码，不代表真实生物学结果。
- `/Download/` 路由引用了 `Download.html`，但仓库中没有这个模板。
- 模板里部分 CSS/JS 使用网络 CDN，离线环境可能加载失败。
- 部分帮助/关于页面文案像是从其他项目迁移来的，还残留 drug/disease 等描述。
- `/znf_summary_json` 当前实现疑似只返回最后一次循环的元素，后续如果页面用到需要重写。
