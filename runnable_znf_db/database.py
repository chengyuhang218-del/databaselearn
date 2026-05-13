import json
import sqlite3

from config import DATABASE_PATH, DATA_DIR


SCHEMA = """
CREATE TABLE IF NOT EXISTS znf (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ensembl TEXT UNIQUE,
    entrez_id TEXT,
    gene_symbol TEXT UNIQUE NOT NULL,
    species TEXT,
    family TEXT,
    proteins TEXT,
    gene_synonym TEXT,
    uniprot_feature TEXT,
    zinc_finger INTEGER
);

CREATE TABLE IF NOT EXISTS chip_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_name TEXT UNIQUE NOT NULL,
    data_source TEXT,
    repeat_number INTEGER,
    peak_number INTEGER,
    znf_gene_symbol TEXT NOT NULL,
    FOREIGN KEY (znf_gene_symbol) REFERENCES znf(gene_symbol)
);

CREATE TABLE IF NOT EXISTS repeat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repeat_name TEXT UNIQUE NOT NULL,
    sub_family TEXT,
    main_family TEXT
);

CREATE TABLE IF NOT EXISTS peak (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chr TEXT,
    start INTEGER,
    end INTEGER,
    strand TEXT,
    enrichment REAL,
    repeat_name TEXT,
    znf_gene_symbol TEXT,
    chip_data_name TEXT,
    FOREIGN KEY (repeat_name) REFERENCES repeat(repeat_name),
    FOREIGN KEY (znf_gene_symbol) REFERENCES znf(gene_symbol),
    FOREIGN KEY (chip_data_name) REFERENCES chip_data(data_name)
);

CREATE TABLE IF NOT EXISTS repeat_region (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chr TEXT,
    start INTEGER,
    end INTEGER,
    strand TEXT,
    repeat_name TEXT,
    znf_gene_symbol TEXT,
    chip_data_name TEXT,
    FOREIGN KEY (repeat_name) REFERENCES repeat(repeat_name),
    FOREIGN KEY (znf_gene_symbol) REFERENCES znf(gene_symbol),
    FOREIGN KEY (chip_data_name) REFERENCES chip_data(data_name)
);

CREATE TABLE IF NOT EXISTS motif (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chip_data_name TEXT UNIQUE,
    raw_motif TEXT,
    full_motif TEXT,
    part_motif TEXT,
    none_motif TEXT,
    FOREIGN KEY (chip_data_name) REFERENCES chip_data(data_name)
);

CREATE TABLE IF NOT EXISTS expression (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ensembl TEXT,
    project TEXT,
    cell_lines TEXT,
    values_json TEXT,
    FOREIGN KEY (ensembl) REFERENCES znf(ensembl)
);

CREATE TABLE IF NOT EXISTS gene_structure (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ensembl TEXT,
    structure_json TEXT,
    FOREIGN KEY (ensembl) REFERENCES znf(ensembl)
);

CREATE TABLE IF NOT EXISTS ortholog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ensembl TEXT,
    scientific_name TEXT,
    ortholog_gene_name TEXT,
    ortholog_id TEXT,
    confidence TEXT,
    FOREIGN KEY (ensembl) REFERENCES znf(ensembl)
);
"""


SAMPLE_ZNFS = [
    {
        "ensembl": "ENSG00000176171",
        "entrez_id": "7739",
        "gene_symbol": "ZNF197",
        "species": "Homo_sapiens",
        "family": "zf-C2H2",
        "proteins": "Q9UK12",
        "gene_synonym": "ZNF166; P18",
        "uniprot_feature": [{"uniprot_id": "Q9UK12", "length": 1021, "zinc_finger": 12}],
        "zinc_finger": 12,
    },
    {
        "ensembl": "ENSG00000198453",
        "entrez_id": "7718",
        "gene_symbol": "ZNF84",
        "species": "Homo_sapiens",
        "family": "zf-C2H2",
        "proteins": "P51523",
        "gene_synonym": "HPF2",
        "uniprot_feature": [{"uniprot_id": "P51523", "length": 733, "zinc_finger": 10}],
        "zinc_finger": 10,
    },
    {
        "ensembl": "ENSG00000197081",
        "entrez_id": "7742",
        "gene_symbol": "ZNF274",
        "species": "Homo_sapiens",
        "family": "zf-C2H2",
        "proteins": "Q96GC6",
        "gene_synonym": "ZKSCAN19",
        "uniprot_feature": [{"uniprot_id": "Q96GC6", "length": 653, "zinc_finger": 5}],
        "zinc_finger": 5,
    },
]

SAMPLE_CHIPS = [
    {"data_name": "GSM2466491", "data_source": "GSE78099", "znf_gene_symbol": "ZNF197"},
    {"data_name": "GSM2466677", "data_source": "GSE78099", "znf_gene_symbol": "ZNF84"},
    {"data_name": "GSM2466514", "data_source": "GSE78099", "znf_gene_symbol": "ZNF274"},
]

SAMPLE_REPEATS = [
    {"repeat_name": "L1PA7", "sub_family": "L1", "main_family": "LINE"},
    {"repeat_name": "AluY", "sub_family": "Alu", "main_family": "SINE"},
    {"repeat_name": "MER11A", "sub_family": "ERVK", "main_family": "LTR"},
    {"repeat_name": "SVA_D", "sub_family": "SVA", "main_family": "Retroposon"},
]

SAMPLE_PEAKS = [
    ("chr1", 120045, 120420, "+", 18.4, "L1PA7", "ZNF197", "GSM2466491"),
    ("chr1", 220010, 220388, "-", 12.1, "AluY", "ZNF197", "GSM2466491"),
    ("chr7", 991000, 991430, "+", 9.6, "MER11A", "ZNF197", "GSM2466491"),
    ("chr3", 510900, 511280, "+", 21.7, "AluY", "ZNF84", "GSM2466677"),
    ("chr5", 781400, 781850, "-", 15.2, "SVA_D", "ZNF84", "GSM2466677"),
    ("chr19", 338000, 338290, "+", 7.8, "L1PA7", "ZNF274", "GSM2466514"),
]


def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.executescript(SCHEMA)
        seed_db(conn)


def seed_db(conn):
    count = conn.execute("SELECT COUNT(*) AS n FROM znf").fetchone()["n"]
    if count:
        return

    for item in SAMPLE_ZNFS:
        conn.execute(
            """
            INSERT INTO znf
            (ensembl, entrez_id, gene_symbol, species, family, proteins, gene_synonym, uniprot_feature, zinc_finger)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["ensembl"],
                item["entrez_id"],
                item["gene_symbol"],
                item["species"],
                item["family"],
                item["proteins"],
                item["gene_synonym"],
                json.dumps(item["uniprot_feature"], ensure_ascii=False),
                item["zinc_finger"],
            ),
        )

    for item in SAMPLE_REPEATS:
        conn.execute(
            "INSERT INTO repeat (repeat_name, sub_family, main_family) VALUES (?, ?, ?)",
            (item["repeat_name"], item["sub_family"], item["main_family"]),
        )

    for item in SAMPLE_CHIPS:
        peak_count = sum(1 for peak in SAMPLE_PEAKS if peak[7] == item["data_name"])
        repeat_count = len({peak[5] for peak in SAMPLE_PEAKS if peak[7] == item["data_name"]})
        conn.execute(
            """
            INSERT INTO chip_data (data_name, data_source, repeat_number, peak_number, znf_gene_symbol)
            VALUES (?, ?, ?, ?, ?)
            """,
            (item["data_name"], item["data_source"], repeat_count, peak_count, item["znf_gene_symbol"]),
        )

    for peak in SAMPLE_PEAKS:
        conn.execute(
            """
            INSERT INTO peak (chr, start, end, strand, enrichment, repeat_name, znf_gene_symbol, chip_data_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            peak,
        )
        conn.execute(
            """
            INSERT INTO repeat_region (chr, start, end, strand, repeat_name, znf_gene_symbol, chip_data_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (peak[0], peak[1] + 30, peak[2] - 30, peak[3], peak[5], peak[6], peak[7]),
        )

    for chip in SAMPLE_CHIPS:
        conn.execute(
            """
            INSERT INTO motif (chip_data_name, raw_motif, full_motif, part_motif, none_motif)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                chip["data_name"],
                "A C T G G A",
                "C C T G A A",
                "A G G T C A",
                "T T C A G G",
            ),
        )

    for znf in SAMPLE_ZNFS:
        conn.execute(
            """
            INSERT INTO expression (ensembl, project, cell_lines, values_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                znf["ensembl"],
                "E-MTAB-4748-demo",
                json.dumps(["K562", "HEK293", "HepG2"], ensure_ascii=False),
                json.dumps([4.2, 7.8, 2.9]),
            ),
        )
        conn.execute(
            """
            INSERT INTO gene_structure (ensembl, structure_json)
            VALUES (?, ?)
            """,
            (
                znf["ensembl"],
                json.dumps(
                    {
                        "gene_start": 100000,
                        "gene_end": 126000,
                        "exons": [
                            {"start": 100000, "end": 101200},
                            {"start": 108500, "end": 109300},
                            {"start": 124000, "end": 126000},
                        ],
                    },
                    ensure_ascii=False,
                ),
            ),
        )
        conn.execute(
            """
            INSERT INTO ortholog (ensembl, scientific_name, ortholog_gene_name, ortholog_id, confidence)
            VALUES (?, ?, ?, ?, ?)
            """,
            (znf["ensembl"], "Mus musculus", znf["gene_symbol"].title(), "ENSMUSG-demo", "high"),
        )

    conn.commit()


def rows(query, params=()):
    with connect() as conn:
        return [dict(row) for row in conn.execute(query, params).fetchall()]


def row(query, params=()):
    with connect() as conn:
        item = conn.execute(query, params).fetchone()
        return dict(item) if item else None
