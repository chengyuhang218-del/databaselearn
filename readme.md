# KRAB DB 项目学习路线

这份路线适合从“能看懂项目结构”开始，慢慢学到“能改页面、改接口、理解数据库和导入脚本”。不要一上来就钻 `import_data.py`，它最长、最依赖生信原始数据，适合放到后面。

## 0. 先建立整体印象

先看文件：

1. `README.md`
2. `MODULES.md`
3. 项目根目录结构

你要先明白这个项目是什么：

- 这是一个 Flask 网站。
- 前端页面在 `templates/`。
- CSS、JS、图片、老师给的静态数据在 `static/`。
- 后端路由和接口主要在 `routes.py`。
- 数据库表结构在 `ZFWebDatabase.py`。
- 老师原始数据导入逻辑在 `import_data.py`。
- 没有完整真实数据时，`seed_demo_data.py` 用来造一份演示数据，把网站先跑通。

这一阶段不用看懂每一行，只要能回答：

- 用户打开 `/KZFP/` 时，大概由哪个文件负责？
- 页面 HTML 在哪里？
- 数据库表在哪里定义？
- 老师新给的 `znf_summary.table` 和 `znf_family.json` 放在哪里？

## 1. 第一个真正看的文件：`app.py`

从 `app.py` 开始，因为它最短，是整个 Flask 应用入口。

重点看：

```python
from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "cyh666"

import routes
```

要理解的基础概念：

- `Flask(__name__)`：创建一个 Flask 应用对象。
- `SECRET_KEY`：表单 CSRF、session 等功能会用到。
- `import routes`：把 `routes.py` 里的路由注册到这个 app 上。
- 应用入口：运行 `flask --app app run` 时，Flask 会找到这里的 `app` 变量。

小练习：

- 在纸上画一句话：`app.py 创建 app，routes.py 给 app 添加网址规则。`

## 2. 第二个文件：`routes.py`，先只看路由列表

不要先看函数内部细节，先搜索：

```text
@app.route
```

你会看到很多网址，例如：

- `/`
- `/index/`
- `/KZFP/`
- `/Repeat/`
- `/searchZnf`
- `/KZFP/zinc_fingure/<data_name>`
- `/repeatDataJson/`
- `/znf_summary_json`
- `/znf_family_json`

要理解的基础概念：

- 路由：网址和 Python 函数的对应关系。
- GET 请求：浏览器打开页面、表格拉取数据常用。
- POST 请求：表单提交常用。
- `render_template()`：返回一个 HTML 页面。
- `jsonify()`：返回 JSON 数据，通常给前端表格或 Ajax 使用。
- URL 参数：`/KZFP/zinc_fingure/<data_name>` 中的 `<data_name>` 会传给函数。

建议先按这个顺序看：

1. `index()`：首页怎么返回。
2. `kzfp()`：KZFP 页面怎么返回。
3. `repeat_page()`：Repeat 页面怎么返回。
4. `kzfpData()`：KZFP 表格数据接口。
5. `query()`：`/znf_summary_json`，读取老师给的 summary 数据。
6. `znf_family_json()`：读取老师给的 family JSON。
7. `searchZnf()`：搜索框提交后怎么处理。
8. `kzfp_one(data_name)`：进入某个 ZNF/ChIP 详情页后做了什么。

小练习：

- 找出 `/KZFP/` 对应的函数名。
- 找出 KZFP 表格请求的是哪个 JSON 接口。
- 找出 `znf_summary.table` 是在哪个函数里被读取的。

## 3. 第三个文件：`templates/base.html`

`base.html` 是所有页面的公共外壳。

重点看：

- `<head>` 里引入了哪些 CSS 和 JS。
- 导航栏里有哪些链接。
- `{% block content %}{% endblock %}`
- `{% block javascript_f %}{% endblock %}`

要理解的基础概念：

- HTML：页面结构。
- CSS：页面样式。
- JavaScript：页面交互。
- Jinja2 模板继承：子页面可以继承 `base.html`，再填充自己的内容。
- `url_for('index')`：Flask 根据函数名生成 URL。

小练习：

- 找出导航栏里的 KZFP 链接。
- 找出页面正文是通过哪个 block 填进去的。

## 4. 第四个文件：`templates/KZFP.html`

这是最适合入门的业务页面，因为它连接了“页面、搜索框、表格、后端 JSON 接口”。

重点看：

- `{% extends "base.html" %}`：继承公共模板。
- 搜索表单：`<form action="/searchZnf" method="post">`
- 表格占位：`<table id="table_1"></table>`
- JavaScript 中的 `$('#table_1').bootstrapTable({...})`
- `url: '/znf_summary_json'`
- `columns` 里每一列的 `field`

要理解的基础概念：

- 表单提交：用户输入 ZNF 名称后提交到 `/searchZnf`。
- Bootstrap Table：前端表格组件。
- 前后端字段对应：前端的 `field: 'znf_name'` 必须对应后端 JSON 里的 `znf_name`。
- 分页接口格式：后端返回 `{"total": 数量, "rows": [...]}`。

老师新数据相关：

- `KZFP.html` 里的表格现在请求 `/znf_summary_json`。
- `/znf_summary_json` 会读取 `static/znf_summary.table`。
- 所以 KZFP 首页表格展示的是老师给的 summary 数据。

小练习：

- 找出 KZFP 表格一共有几列。
- 找出哪一列点击后会跳转到 `/KZFP/zinc_fingure/<data_no>`。
- 对照 `znf_summary.table` 的表头，看它们和 `columns` 里的字段是否一致。

## 5. 第五步：理解 `static/znf_summary.table` 和 `static/znf_family.json`

先看：

1. `static/znf_summary.table`
2. `static/znf_family.json`

`znf_summary.table` 是制表符分隔文本，不是数据库表。它的字段包括：

- `znf_name`
- `data_no`
- `data_source`
- `peak_number`
- `repeat_number`
- `motif_all_img_path`

`znf_family.json` 是 JSON 文件，内容结构和 summary 很接近，适合直接作为接口数据返回。

要理解的基础概念：

- TSV：Tab-Separated Values，制表符分隔文本。
- JSON：前后端常用的数据交换格式。
- 静态文件和数据库的区别：
  - 静态文件适合直接读取、展示、下载。
  - 数据库适合复杂查询、关联、增删改。

小练习：

- 用记事本打开 `znf_summary.table`，找到第一行表头。
- 找到第一条数据 `ZNF479`，看它的 `data_no` 是什么。

## 6. 第六个文件：`ZFWebDatabase.py`

这个文件是数据库模型，开始会有点难，但它是理解项目“数据关系”的核心。

建议先看这些类：

1. `Znf`
2. `Chip_data`
3. `Repeat`
4. `Peaks`
5. `Repeat_region`
6. `Motif`
7. `Expression`
8. `Gene_structure`
9. `Orthologs`
10. `AccurityWebDB`

要理解的基础概念：

- ORM：用 Python 类表示数据库表。
- 表：例如 `znf`、`chip_data`、`repeat`。
- 字段：例如 `gene_symbol`、`data_name`、`peak_number`。
- 主键：通常是 `id`。
- 外键：一张表关联另一张表。
- 一对多：一个 ZNF 可以有多个 ChIP 数据。
- 多对多：一个 ZNF 可以关联多个 Repeat，一个 Repeat 也可以关联多个 ZNF。
- `relationship()`：SQLAlchemy 用来描述表之间的关系。
- `session`：数据库操作上下文，用来查询、添加、提交。

建议画出这条主线：

```text
Znf
  -> Chip_data
      -> Peaks
          -> Repeat

Znf
  -> Repeat
```

小练习：

- 找出 `Znf` 类对应的数据库表名。
- 找出 `Chip_data` 是通过哪个字段关联到 `Znf` 的。
- 找出 `Peaks` 同时关联了哪三类数据。

## 7. 第七个文件：`seed_demo_data.py`

这个文件比 `import_data.py` 更适合学习，因为它数据少、逻辑完整。

重点看：

- 它怎么创建一个 `Znf`。
- 它怎么创建一个 `Repeat`。
- 它怎么创建一个 `Chip_data`。
- 它怎么把它们关联起来。
- 它怎么创建 `Peaks`、`Motif`、`Expression`、`Gene_structure`。
- 它最后怎么 `session.add()` 和 `session.commit()`。

要理解的基础概念：

- 创建 ORM 对象。
- 设置对象属性。
- 设置对象之间的关系。
- 提交事务。
- 演示数据和真实数据的区别。

小练习：

- 找出演示 ZNF 的名字。
- 找出演示 ChIP 数据集的 `data_name`。
- 找出详情页 `/KZFP/zinc_fingure/GSMDEMO001` 为什么能打开。

## 8. 第八个文件：`templates/one_znf.html` 或 `templates/oneZnf.html`

这个阶段开始看详情页。

后端入口是：

```text
/KZFP/zinc_fingure/<data_name>
```

对应函数是：

```python
kzfp_one(data_name)
```

你要把这两部分连起来看：

1. `routes.py` 里的 `kzfp_one(data_name)`
2. `templates/one_znf.html` 或 `templates/oneZnf.html`

要理解的基础概念：

- 后端把数据整理成字典，例如 `znf_data`。
- 模板通过 `{{ znf_data["gene_symbol"] }}` 取值。
- 详情页不只是展示静态文本，还会展示 repeat 统计、表达、基因结构等。

小练习：

- 找出 `znf_data["gene_symbol"]` 在后端哪里赋值。
- 找出它在模板哪里显示。

## 9. 第九个文件：`templates/Repeat.html` 和 Repeat 相关路由

看 Repeat 页面时，重点对应这些函数：

- `repeat_page()`
- `searchRepeat()`
- `repeatDataJson()`
- `repeat_one(repeat_id)`
- `oneRepeatDataJson(repeat_id)`

要理解的基础概念：

- 同一个页面可以有表格列表，也可以有搜索框。
- 列表页通常请求 JSON API。
- 详情页通常根据 ID 查数据库。

小练习：

- 找出 Repeat 列表页请求哪个接口。
- 找出搜索 Repeat 时查的是哪个字段。

## 10. 最后再看：`import_data.py`

这个文件放最后，因为它依赖大量外部原始数据路径。

建议先只看函数名和导入顺序：

1. `C2H2_information()`
2. `import_basic_information()`
3. `import_repeat()`
4. `import_peaks()`
5. `import_expression()`
6. `import_gene_structure()`
7. `import_orthologs()`

要理解的基础概念：

- 数据清洗：把原始文本、表格、JSON 变成统一结构。
- pandas：读取表格数据、筛选行列。
- 批量导入：循环读取很多文件，写入数据库。
- 生信数据路径：老师代码里很多路径是 Linux 机器路径，需要改成本机路径。
- 导入顺序很重要：必须先有 ZNF，再能关联 Chip、Repeat、Peaks。

小练习：

- 找出 `parse_GSE78099()` 解析出来的列名。
- 找出 `import_repeat()` 为什么需要先查 `Znf`。
- 找出 `import_peaks()` 里 peak、repeat、chip_data 是怎么关联的。

## 11. 学这个项目前最好补的基础

### Python 基础

需要会：

- 变量、列表、字典
- 函数
- 类和对象
- 文件读取
- `import`
- 异常报错怎么看

重点例子：

```python
row["znf_name"]
data.append(row)
for item in all_znf:
    ...
```

### Web 基础

需要明白：

- 浏览器访问 URL。
- 后端接收请求。
- 后端返回 HTML 或 JSON。
- HTML 负责结构。
- CSS 负责样式。
- JavaScript 负责交互。

### Flask 基础

需要明白：

- `Flask`
- `@app.route`
- `request`
- `render_template`
- `jsonify`
- 表单 POST
- URL 参数

### HTML / Jinja2 基础

需要明白：

- 标签：`div`、`table`、`form`、`input`
- 模板继承：`extends`
- 内容块：`block`
- 变量输出：`{{ ... }}`
- 控制语句：`{% ... %}`

### JavaScript / Bootstrap Table 基础

需要明白：

- jQuery 的 `$()`
- 页面加载后执行函数
- Ajax 请求 JSON
- 表格列 `columns`
- 分页参数 `limit` 和 `offset`

### SQL 和 SQLAlchemy 基础

需要明白：

- 数据库、表、字段
- 主键、外键
- 一对多、多对多
- 查询：`filter_by`
- 新增：`session.add`
- 保存：`session.commit`
- ORM 类和数据库表的对应关系

### 生物信息学背景概念

不用一开始很深，但至少知道：

- ZNF：Zinc Finger protein，锌指蛋白。
- KRAB-ZFP：带 KRAB 结构域的锌指蛋白。
- ChIP-seq：研究蛋白和 DNA 结合位置的实验数据。
- peak：ChIP-seq 中检测到的结合峰区域。
- repeat / repetitive sequence：重复序列。
- motif：序列模式或结合偏好。
- Ensembl ID：基因数据库编号。
- orthologs：不同物种中的同源基因。
- expression：基因表达数据。

## 12. 推荐学习顺序总表

| 顺序 | 文件/目录 | 目标 |
|---|---|---|
| 1 | `README.md` | 知道项目怎么跑、有哪些模块 |
| 2 | `MODULES.md` | 建立模块地图 |
| 3 | `app.py` | 理解 Flask 入口 |
| 4 | `routes.py` 路由列表 | 理解 URL 和函数的对应关系 |
| 5 | `templates/base.html` | 理解公共页面结构 |
| 6 | `templates/KZFP.html` | 理解一个完整列表页 |
| 7 | `static/znf_summary.table` | 理解老师提供的新 summary 数据 |
| 8 | `static/znf_family.json` | 理解 JSON 静态数据 |
| 9 | `ZFWebDatabase.py` | 理解数据库表和关系 |
| 10 | `seed_demo_data.py` | 理解如何造数据、写数据库 |
| 11 | `one_znf.html` / `oneZnf.html` | 理解详情页 |
| 12 | `Repeat.html` 和 Repeat 路由 | 理解第二条业务线 |
| 13 | `import_data.py` | 理解真实数据导入 |

## 13. 每学完一轮，你应该能做到什么

第一轮：看懂结构

- 知道每个文件大概负责什么。
- 知道页面、接口、数据库模型分别在哪里。

第二轮：看懂页面流转

- 能说清楚打开 `/KZFP/` 后发生了什么。
- 能说清楚表格数据从哪里来。
- 能说清楚搜索框提交到哪里。

第三轮：看懂数据库

- 能说清楚 `Znf`、`Chip_data`、`Repeat`、`Peaks` 的关系。
- 能跟着 `seed_demo_data.py` 看懂一条演示数据如何写入数据库。

第四轮：能做小修改

- 改一个表格列名。
- 增加一个 JSON 接口。
- 改一个搜索逻辑。
- 把一个静态数据文件接到页面上。

第五轮：能理解复现难点

- 知道为什么 `import_data.py` 不能直接跑。
- 知道缺哪些老师原始数据。
- 知道哪些路径要改成本机路径。
- 知道完整导入时为什么有先后顺序。

## 14. 最适合你的第一天学习任务

今天只做这几件事就够：

1. 看 `app.py`，明白它怎么创建 Flask app。
2. 在 `routes.py` 里搜索 `@app.route`，列出所有网址。
3. 看 `templates/KZFP.html`，找到表格请求的 `/znf_summary_json`。
4. 打开 `static/znf_summary.table`，对照表头和 KZFP 表格列。
5. 在笔记里画一条链：

```text
浏览器打开 /KZFP/
  -> routes.py 的 kzfp()
  -> templates/KZFP.html
  -> 前端表格请求 /znf_summary_json
  -> routes.py 读取 static/znf_summary.table
  -> 返回 JSON
  -> 页面显示表格
```

把这条链真正想明白，你就已经摸到这个项目的主干了。
