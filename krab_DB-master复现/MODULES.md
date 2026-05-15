# 代码模块说明

## app.py

Flask 应用入口。老师的 `routes.py` 里写了 `from app import app`，但原文件夹没有提供 `app.py`，所以这里补了一个最小入口。

运行网站：

```powershell
flask --app app run
```

## ZFWebDatabase.py

核心数据库模型文件，使用 SQLAlchemy ORM 定义表结构和关系。

主要表模型：

- `Znf`：ZNF 基本信息，包含 `ensembl`、`entrez_id`、`gene_symbol`、`species`、`family`、`proteins`、`gene_synonym`、`unipro_feature`。
- `Chip_data`：ChIP-seq 数据集信息，包含 `data_name`、`data_source`、`repeat_number`、`peak_number`，通过 `znf_gene_symbol` 关联 `Znf`。
- `Repeat`：重复序列信息，包含 `repeat_name`、`sub_family`、`main_family`、`znf_number`。
- `Repeat_family`：Repeat 的家族分类扩展表。
- `Peaks`：peak 区域信息，包含染色体、起止位置、链方向、富集度，并关联 ZNF、Repeat、Chip_data。
- `Repeat_region`：Repeat 在基因组上的区域。
- `Motif`：motif 图片和矩阵文件路径。
- `C2H2`：C2H2 转录因子信息。
- `Expression`：表达矩阵，按 Ensembl 和 project 保存 JSON 字符串。
- `Gene_structure`：基因结构，保存转录本和 exon JSON。
- `Cell_line`：表达项目的细胞系列表。
- `Orthologs`：同源基因信息。

关系表：

- `znf_repeat`：`Znf` 与 `Repeat` 多对多。
- `chip_data_repeat`：`Chip_data` 与 `Repeat` 多对多。
- `znf_repeatRegion`：`Znf` 与 `Repeat_region` 多对多。
- `chipData_repeatRegion`：`Chip_data` 与 `Repeat_region` 多对多。

封装类：

- `AccurityWebDB`：负责连接数据库、创建/删除表、创建 session，并提供 `getZnf()`、`getChip_data()`、`getRepeat()` 等查重式创建方法。

## import_data.py

老师原始数据库构建脚本。主要职责是读取外部生信结果文件，解析成 ORM 对象并写入 PostgreSQL。

关键方法：

- `parse_GSE78099()`：解析 GSE78099 的 peak 与 repeat overlap 表。
- `parseUniprot()`：解析 UniProt C2H2 注释。
- `C2H2_information()`：整合 UniProt、Ensembl mapping、人/鼠 TF 列表，生成基础 ZNF 信息。
- `import_basic_information()`：导入 `Znf` 表。
- `import_repeat()`：导入 `Repeat` 和 `Chip_data` 基础关系。
- `import_peaks()`：导入 peak、repeat region、repeat family 等核心数据。
- `import_expression()`：导入表达矩阵和细胞系。
- `import_gene_structure()`：导入转录本和 exon 结构。
- `import_orthologs()`：导入同源基因。

脚本底部会先 `dropAll()` 删除旧表，再 `CreateAllTable()` 重建并导入全部数据。学习时建议先注释掉 `dropAll()`，避免误删已有数据库。

## seed_demo_data.py

新增的演示数据脚本。它不替代老师的 `import_data.py`，只是在没有真实数据集时插入一组最小数据，让页面可以打开和联动。

它会创建：

- `Znf`：`ZNFDEMO1`
- `Repeat` / `Repeat_family`：`DEMO_REPEAT_A`
- `Chip_data`：`GSMDEMO001`
- `Peaks` 和 `Repeat_region`：3 条示例记录
- `Motif`：指向生成的静态 motif 占位文件
- `Cell_line`、`Expression`、`Gene_structure`、`Orthologs`

运行：

```powershell
python seed_demo_data.py
```

重建演示数据：

```powershell
python seed_demo_data.py --refresh-demo
```

## routes.py

网站路由和 API 层。启动时连接 PostgreSQL 并创建全局 session。

页面路由：

- `/`、`/index/`：首页。
- `/KZFP/`：ZNF/KZFP 搜索页。
- `/Repeat/`：Repeat 搜索页。
- `/Expression/`：表达页面。
- `/Help/`：帮助页面。
- `/About/`：关于页面。
- `/Download/`：下载页面，但当前缺少 `Download.html`。

查询路由：

- `/searchZnf`：表单提交 ZNF 名称，查 `Znf.gene_symbol`。
- `/searchRepeat`：表单提交 Repeat 名称，查 `Repeat.repeat_name`。
- `/KZFP/zinc_fingure/<data_name>`：展示单个 ChIP 数据关联的 ZNF 详情、repeat 统计、表达和基因结构。
- `/Repeat/repeat_one/<repeat_id>`：展示单个 Repeat 详情。

JSON API：

- `/repeatDataJson/`：Repeat 列表，给 bootstrap-table 使用。
- `/oneRepeatDataJson/<repeat_id>`：单个 Repeat 关联的 peak 列表。
- `/kzpfdatajson/`：ChIP/ZNF 数据集列表。
- `/znf_summary_json`：ZNF summary JSON，当前实现疑似未完成。
- `/searchorthologs`：按 Ensembl 返回同源基因信息。

## templates/

Jinja2 页面模板。

- `base.html`：公共导航栏和基础 CSS/JS 引用。
- `index.html` / `iindex.html`：首页相关模板。
- `KZFP.html`：ZNF/KZFP 搜索和列表。
- `Repeat.html`：Repeat 搜索和列表。
- `one_znf.html` / `oneZnf.html`：单个 ZNF 详情页，两个文件内容接近。
- `one_repeat.html`：单个 Repeat 详情页。
- `expression.html`：表达相关页面。
- `help.html`、`about.html`：帮助和介绍页面。
- `No_result.html`：无结果页。

## static/

前端静态文件和部分预计算 summary。

- `bootstrap.css`、`bootstrap.js`、`bootstrap-table.min.*`、`jquery-3.4.1.min.js`：前端依赖。
- `logo1.png`：项目 logo。
- `znf_summary.table`：ZNF 数据 summary 表。
- `znf_family.json`：ZNF summary JSON 数据。
- `static/img/GSEDEMO_out/...`：运行 `seed_demo_data.py` 后生成的演示 motif 文件目录。

## database/

旧版/备份代码目录，包含另一份 `ZFWebDatabase.py` 和 `import_data.py`。这两份模型比根目录版本少一些字段/表，学习和复现时建议以根目录文件为准。
