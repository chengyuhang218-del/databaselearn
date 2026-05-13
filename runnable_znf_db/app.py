import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, unquote, urlparse

from config import DEMO_DB, PROJECT_INFO
from database import init_db, row, rows


HOST = "127.0.0.1"
PORT = 5050


def page(title, body):
    return f"""<!doctype html>
<html lang="zh">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: light; --ink:#1f2937; --muted:#64748b; --line:#d8dee9; --brand:#0f766e; --soft:#f1f5f9; }}
    body {{ margin:0; font-family: Arial, "PingFang SC", "Microsoft YaHei", sans-serif; color:var(--ink); background:#fbfdff; }}
    header {{ background:#102a43; color:white; padding:18px 0; }}
    main, .nav-inner {{ width:min(1100px, calc(100% - 32px)); margin:auto; }}
    nav {{ display:flex; align-items:center; justify-content:space-between; gap:18px; }}
    nav a {{ color:white; text-decoration:none; margin-left:18px; font-weight:600; }}
    h1 {{ margin:28px 0 12px; font-size:30px; }}
    h2 {{ margin:28px 0 10px; font-size:22px; }}
    p {{ line-height:1.75; }}
    .muted {{ color:var(--muted); }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:14px; }}
    .card {{ background:white; border:1px solid var(--line); border-radius:8px; padding:16px; }}
    .metric {{ font-size:28px; font-weight:700; color:var(--brand); }}
    table {{ width:100%; border-collapse:collapse; background:white; border:1px solid var(--line); }}
    th, td {{ padding:10px 12px; border-bottom:1px solid var(--line); text-align:left; }}
    th {{ background:var(--soft); }}
    input {{ padding:10px 12px; border:1px solid var(--line); border-radius:6px; min-width:260px; }}
    button, .button {{ padding:10px 14px; border:0; border-radius:6px; background:var(--brand); color:white; text-decoration:none; cursor:pointer; }}
    code {{ background:var(--soft); padding:2px 5px; border-radius:4px; }}
    .bar {{ height:12px; background:#dbeafe; border-radius:20px; overflow:hidden; }}
    .bar span {{ display:block; height:100%; background:#0f766e; }}
    footer {{ margin-top:40px; padding:20px 0; border-top:1px solid var(--line); color:var(--muted); }}
  </style>
</head>
<body>
  <header>
    <div class="nav-inner">
      <nav>
        <strong>{html.escape(PROJECT_INFO["name"])}</strong>
        <div>
          <a href="/">首页</a>
          <a href="/kzfp">KZFP</a>
          <a href="/repeat">Repeat</a>
          <a href="/about">配置说明</a>
        </div>
      </nav>
    </div>
  </header>
  <main>{body}</main>
  <footer><main>本地教学复现版，默认使用 SQLite 模拟数据库。</main></footer>
</body>
</html>"""


def table(items, columns):
    if not items:
        return "<p class='muted'>暂无数据。</p>"
    head = "".join(f"<th>{html.escape(label)}</th>" for _, label in columns)
    body = []
    for item in items:
        cells = []
        for key, _ in columns:
            value = item.get(key, "")
            cells.append(f"<td>{value}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return "<table><thead><tr>" + head + "</tr></thead><tbody>" + "".join(body) + "</tbody></table>"


def home():
    znf_count = row("SELECT COUNT(*) AS n FROM znf")["n"]
    peak_count = row("SELECT COUNT(*) AS n FROM peak")["n"]
    repeat_count = row("SELECT COUNT(*) AS n FROM repeat")["n"]
    chip_count = row("SELECT COUNT(*) AS n FROM chip_data")["n"]
    body = f"""
      <h1>{html.escape(PROJECT_INFO["full_name"])}</h1>
      <p class="muted">{html.escape(PROJECT_INFO["source_note"])}</p>
      <section class="grid">
        <div class="card"><div class="metric">{znf_count}</div><div>ZNF genes</div></div>
        <div class="card"><div class="metric">{chip_count}</div><div>ChIP-seq datasets</div></div>
        <div class="card"><div class="metric">{peak_count}</div><div>Peak records</div></div>
        <div class="card"><div class="metric">{repeat_count}</div><div>Repeat classes</div></div>
      </section>
      <h2>搜索 ZNF</h2>
      <form action="/search_znf" method="get">
        <input name="q" placeholder="输入 ZNF197、ZNF84 或 ZNF274">
        <button type="submit">搜索</button>
      </form>
      <h2>复现目标</h2>
      <p>这个版本用模拟数据跑通完整闭环：ZNF 基础信息、ChIP-seq 数据、peak、repeat、motif、表达量、基因结构和 orthologs。后续只要把 <code>database.py</code> 中的模拟数据替换为真实导入脚本，就能对接老师项目的数据处理流程。</p>
    """
    return page("首页", body)


def kzfp():
    items = rows(
        """
        SELECT z.gene_symbol, z.ensembl, z.family, c.data_name, c.data_source, c.peak_number, c.repeat_number
        FROM znf z
        LEFT JOIN chip_data c ON c.znf_gene_symbol = z.gene_symbol
        ORDER BY z.gene_symbol
        """
    )
    for item in items:
        symbol = quote(item["gene_symbol"])
        item["gene_symbol"] = f'<a href="/znf?symbol={symbol}">{html.escape(item["gene_symbol"])}</a>'
    body = "<h1>KZFP / ZNF 总览</h1>" + table(
        items,
        [
            ("gene_symbol", "ZNF"),
            ("ensembl", "Ensembl"),
            ("family", "Family"),
            ("data_name", "Data No."),
            ("data_source", "Source"),
            ("peak_number", "Peaks"),
            ("repeat_number", "Repeats"),
        ],
    )
    return page("KZFP", body)


def repeat_page():
    items = rows(
        """
        SELECT r.id, r.repeat_name, r.sub_family, r.main_family,
               COUNT(DISTINCT p.znf_gene_symbol) AS znf_number,
               COUNT(p.id) AS peak_number
        FROM repeat r
        LEFT JOIN peak p ON p.repeat_name = r.repeat_name
        GROUP BY r.id
        ORDER BY r.repeat_name
        """
    )
    for item in items:
        item["repeat_name"] = f'<a href="/repeat_one?id={item["id"]}">{html.escape(item["repeat_name"])}</a>'
    body = "<h1>Repeat 总览</h1>" + table(
        items,
        [
            ("repeat_name", "Repeat"),
            ("sub_family", "Sub family"),
            ("main_family", "Main family"),
            ("znf_number", "Related ZNF"),
            ("peak_number", "Overlapped peaks"),
        ],
    )
    return page("Repeat", body)


def znf_detail(symbol):
    item = row("SELECT * FROM znf WHERE gene_symbol = ?", (symbol,))
    if not item:
        return page("未找到", "<h1>没有找到这个 ZNF</h1><p><a href='/kzfp'>返回 KZFP 列表</a></p>")
    chip = row("SELECT * FROM chip_data WHERE znf_gene_symbol = ?", (symbol,))
    peaks = rows("SELECT * FROM peak WHERE znf_gene_symbol = ? ORDER BY enrichment DESC", (symbol,))
    expression = row("SELECT * FROM expression WHERE ensembl = ?", (item["ensembl"],))
    structure = row("SELECT * FROM gene_structure WHERE ensembl = ?", (item["ensembl"],))
    orthologs = rows("SELECT * FROM ortholog WHERE ensembl = ?", (item["ensembl"],))
    repeat_counts = rows(
        """
        SELECT repeat_name, COUNT(*) AS n
        FROM peak
        WHERE znf_gene_symbol = ?
        GROUP BY repeat_name
        ORDER BY n DESC
        """,
        (symbol,),
    )
    bars = "".join(
        f"<p>{html.escape(r['repeat_name'])}: {r['n']}</p><div class='bar'><span style='width:{min(r['n'] * 35, 100)}%'></span></div>"
        for r in repeat_counts
    )
    expr = ""
    if expression:
        cells = json.loads(expression["cell_lines"])
        values = json.loads(expression["values_json"])
        expr = table([{"cell": c, "value": v} for c, v in zip(cells, values)], [("cell", "Cell line"), ("value", "TPM demo")])
    gene = ""
    if structure:
        gene = f"<pre>{html.escape(json.dumps(json.loads(structure['structure_json']), ensure_ascii=False, indent=2))}</pre>"
    body = f"""
      <h1>{html.escape(item["gene_symbol"])} 详情</h1>
      <section class="grid">
        <div class="card"><strong>Ensembl</strong><p>{html.escape(item["ensembl"])}</p></div>
        <div class="card"><strong>Entrez ID</strong><p>{html.escape(item["entrez_id"])}</p></div>
        <div class="card"><strong>Zinc fingers</strong><p>{item["zinc_finger"]}</p></div>
        <div class="card"><strong>Dataset</strong><p>{html.escape(chip["data_name"]) if chip else ""}</p></div>
      </section>
      <h2>Repeat overlap 分布</h2>
      {bars or "<p class='muted'>暂无 repeat overlap。</p>"}
      <h2>Peaks</h2>
      {table(peaks, [("chr", "Chr"), ("start", "Start"), ("end", "End"), ("strand", "Strand"), ("enrichment", "Enrichment"), ("repeat_name", "Repeat")])}
      <h2>Expression</h2>
      {expr}
      <h2>Gene structure JSON</h2>
      {gene}
      <h2>Orthologs</h2>
      {table(orthologs, [("scientific_name", "Species"), ("ortholog_gene_name", "Gene"), ("ortholog_id", "Ortholog ID"), ("confidence", "Confidence")])}
    """
    return page(item["gene_symbol"], body)


def repeat_detail(repeat_id):
    item = row("SELECT * FROM repeat WHERE id = ?", (repeat_id,))
    if not item:
        return page("未找到", "<h1>没有找到这个 repeat</h1><p><a href='/repeat'>返回 Repeat 列表</a></p>")
    regions = rows("SELECT * FROM repeat_region WHERE repeat_name = ? ORDER BY chr, start", (item["repeat_name"],))
    body = f"""
      <h1>{html.escape(item["repeat_name"])} 详情</h1>
      <section class="grid">
        <div class="card"><strong>Sub family</strong><p>{html.escape(item["sub_family"])}</p></div>
        <div class="card"><strong>Main family</strong><p>{html.escape(item["main_family"])}</p></div>
        <div class="card"><strong>Region count</strong><p>{len(regions)}</p></div>
      </section>
      <h2>Repeat regions</h2>
      {table(regions, [("chr", "Chr"), ("start", "Start"), ("end", "End"), ("strand", "Strand"), ("znf_gene_symbol", "ZNF"), ("chip_data_name", "Dataset")])}
    """
    return page(item["repeat_name"], body)


def about():
    body = f"""
      <h1>配置说明</h1>
      <p>这个版本已经把原项目中的路径、账号和密码全部改成可迁移配置。</p>
      <table>
        <tr><th>配置项</th><th>当前模拟值</th></tr>
        <tr><td>driver</td><td>{html.escape(DEMO_DB["driver"])}</td></tr>
        <tr><td>host</td><td>{html.escape(DEMO_DB["host"])}</td></tr>
        <tr><td>database</td><td>{html.escape(DEMO_DB["database"])}</td></tr>
        <tr><td>user</td><td>{html.escape(DEMO_DB["user"])}</td></tr>
        <tr><td>password</td><td>{html.escape(DEMO_DB["password"])}</td></tr>
      </table>
      <h2>切换到真实 PostgreSQL 的思路</h2>
      <p>教学版默认用 SQLite，方便直接运行。等你要接真实数据时，可以用 Flask + SQLAlchemy 版本，把数据库连接改成类似 <code>postgresql://znf_demo_user:znf_demo_pass_123@localhost:5432/znf_demo_db</code>，同时把 <code>data/</code> 下的模拟数据替换成老师项目的 GSE78099、UniProt、expression、gene structure 数据。</p>
    """
    return page("配置说明", body)


def api(path):
    if path == "/api/znfs":
        return rows("SELECT * FROM znf ORDER BY gene_symbol")
    if path == "/api/repeats":
        return rows("SELECT * FROM repeat ORDER BY repeat_name")
    if path == "/api/peaks":
        return rows("SELECT * FROM peak ORDER BY id")
    return {"error": "unknown api"}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        if path.startswith("/api/"):
            self.send_json(api(path))
            return
        if path == "/":
            self.send_html(home())
            return
        if path == "/kzfp":
            self.send_html(kzfp())
            return
        if path == "/repeat":
            self.send_html(repeat_page())
            return
        if path == "/znf":
            self.send_html(znf_detail(unquote(params.get("symbol", [""])[0])))
            return
        if path == "/repeat_one":
            self.send_html(repeat_detail(params.get("id", ["0"])[0]))
            return
        if path == "/search_znf":
            self.send_html(znf_detail(unquote(params.get("q", [""])[0].strip())))
            return
        if path == "/about":
            self.send_html(about())
            return
        self.send_html(page("404", "<h1>404</h1><p>页面不存在。</p>"), 404)

    def send_html(self, content, status=200):
        data = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, content, status=200):
        data = json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))


def main():
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"HKZRSdb demo is running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
