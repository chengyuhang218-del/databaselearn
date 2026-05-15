#!/usr/bin/python

import argparse
import base64
import json
import shutil
from pathlib import Path

import ZFWebDatabase as DB


DEMO_ZNF_SYMBOL = "ZNFDEMO1"
DEMO_ENSEMBL = "ENSGDEMO000001"
DEMO_REPEAT_NAME = "DEMO_REPEAT_A"
DEMO_DATA_NAME = "GSMDEMO001"
DEMO_DATA_SOURCE = "GSEDEMO"
DEMO_CELL_LINES = json.dumps(["K562", "HepG2", "HEK293"])
PROJECT_ROOT = Path(__file__).resolve().parent


def connect_db():
    db = DB.AccurityWebDB("cyh666", "666666", "ZNFdb", hostname="localhost")
    db.Connect()
    db.CreateAllTable()
    return db, db.SessionUp()


def create_demo_static_files():
    motif_root = PROJECT_ROOT / "static" / "img" / f"{DEMO_DATA_SOURCE}_out" / f"{DEMO_DATA_NAME}_{DEMO_ZNF_SYMBOL}"
    source_logo = PROJECT_ROOT / "static" / "logo1.png"
    tiny_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAGQAAAAkCAYAAABw4pVUAAAAF0lEQVR42u3BMQEAAADCoPVPbQ0PoAAAAAAAAAB4Gz4kAAE8xGfPAAAAAElFTkSuQmCC"
    )

    for motif_type in ["raw", "none", "part", "full"]:
        motif_dir = motif_root / motif_type
        motif_dir.mkdir(parents=True, exist_ok=True)
        logo_path = motif_dir / "logo1.png"
        if source_logo.exists():
            shutil.copyfile(source_logo, logo_path)
        else:
            logo_path.write_bytes(tiny_png)
        (motif_dir / "matrix").write_text(
            "letter-probability matrix: alength= 4 w= 4\n"
            "0.25 0.25 0.25 0.25\n"
            "0.10 0.40 0.40 0.10\n"
            "0.30 0.20 0.20 0.30\n"
            "0.20 0.30 0.30 0.20\n",
            encoding="utf-8",
        )
        (motif_dir / "score").write_text("demo\t3\t0.01\n", encoding="utf-8")


def demo_exists(session):
    return session.query(DB.Znf).filter_by(gene_symbol=DEMO_ZNF_SYMBOL).first() is not None


def clear_demo_data(session):
    demo_chips = session.query(DB.Chip_data).filter_by(data_name=DEMO_DATA_NAME).all()
    for chip in demo_chips:
        chip.repeat.clear()
        chip.repeat_region.clear()
        session.delete(chip)

    demo_repeats = session.query(DB.Repeat).filter_by(repeat_name=DEMO_REPEAT_NAME).all()
    for repeat in demo_repeats:
        repeat.znf.clear()
        for region in list(repeat.repeat_region):
            region.znf.clear()
            region.chip_data.clear()
            session.delete(region)
        if repeat.repeat_family is not None:
            session.delete(repeat.repeat_family)
        session.delete(repeat)

    demo_znfs = session.query(DB.Znf).filter_by(gene_symbol=DEMO_ZNF_SYMBOL).all()
    for znf in demo_znfs:
        znf.repeat.clear()
        znf.repeat_region.clear()
        session.delete(znf)

    session.query(DB.Expression).filter_by(ensembl=DEMO_ENSEMBL).delete()
    session.query(DB.Gene_structure).filter_by(ensembl=DEMO_ENSEMBL).delete()
    session.query(DB.Orthologs).filter_by(ensembl=DEMO_ENSEMBL).delete()
    session.query(DB.Cell_line).filter_by(project="E-MTAB-4748", cell=DEMO_CELL_LINES).delete()
    session.commit()


def seed_demo_data(session):
    znf = DB.Znf(
        ensembl=DEMO_ENSEMBL,
        entrez_id="900001",
        gene_symbol=DEMO_ZNF_SYMBOL,
        species="Homo_sapiens",
        family="zf-C2H2",
        proteins="Demo KRAB zinc finger protein",
        gene_synonym="ZNFDEMO1 DEMO-KRAB",
        unipro_feature=json.dumps([{"uniproID": "PDEMO1", "length": 512, "zinc_finger": 8}]),
    )

    repeat = DB.Repeat(
        repeat_name=DEMO_REPEAT_NAME,
        sub_family="DemoSub",
        main_family="DemoMain",
        znf_number=1,
    )
    repeat.znf.append(znf)

    repeat_family = DB.Repeat_family(
        repeat_name=DEMO_REPEAT_NAME,
        sub_family="DemoSub",
        main_family="DemoMain",
    )
    repeat_family.repeat = repeat

    chip_data = DB.Chip_data(
        data_name=DEMO_DATA_NAME,
        data_source=DEMO_DATA_SOURCE,
        repeat_number=1,
        peak_number=3,
    )
    chip_data.znf = znf
    chip_data.repeat.append(repeat)

    motif_base = f"/static/img/{DEMO_DATA_SOURCE}_out/{DEMO_DATA_NAME}_{DEMO_ZNF_SYMBOL}"
    motif = DB.Motif(
        znf_all_motif_img_path=f"{motif_base}/raw/logo1.png",
        znf_all_motif_matrix_path=f"{motif_base}/raw/matrix",
        znf_full_motif_img_path=f"{motif_base}/full/logo1.png",
        znf_full_motif_matrix_path=f"{motif_base}/full/matrix",
        znf_part_motif_img_path=f"{motif_base}/part/logo1.png",
        znf_part_motif_matrix_path=f"{motif_base}/part/matrix",
        znf_None_motif_img_path=f"{motif_base}/none/logo1.png",
        znf_None_motif_matrix_path=f"{motif_base}/none/matrix",
    )
    motif.chip_data = chip_data

    peak_rows = [
        ("chr1", 100000, 100240, "+", 12.5, 100120, 100210),
        ("chr1", 101000, 101260, "+", 8.7, 101080, 101190),
        ("chr2", 205000, 205310, "-", 15.2, 205040, 205250),
    ]
    for chrom, start, end, strand, enrichment, repeat_start, repeat_end in peak_rows:
        peak = DB.Peaks(
            chr=chrom,
            start=start,
            end=end,
            strand=strand,
            enrichment=enrichment,
            ensembl=DEMO_ENSEMBL,
        )
        peak.chip_data = chip_data
        peak.repeat = repeat
        peak.znf = znf

        region = DB.Repeat_region(
            chr=chrom,
            start=repeat_start,
            end=repeat_end,
            strand=strand,
        )
        region.repeat = repeat
        region.znf.append(znf)
        region.chip_data.append(chip_data)
        session.add_all([peak, region])

    cell_line = DB.Cell_line(
        project="E-MTAB-4748",
        cell=DEMO_CELL_LINES,
    )
    expression = DB.Expression(
        ensembl=DEMO_ENSEMBL,
        project="E-MTAB-4748",
        expression=json.dumps([6.2, 3.8, 1.4]),
    )

    gene_structure = DB.Gene_structure(
        ensembl=DEMO_ENSEMBL,
        structure=json.dumps(
            {
                "ensembl_gene_id": DEMO_ENSEMBL,
                "Transcripts": [
                    {
                        "ensembl_transcript_id": "ENSTDEMO000001",
                        "start_position": 100000,
                        "end_position": 106000,
                        "exons": [
                            {"exon_chrom_start": 100000, "exon_chrom_end": 100550},
                            {"exon_chrom_start": 102000, "exon_chrom_end": 102420},
                            {"exon_chrom_start": 105300, "exon_chrom_end": 106000},
                        ],
                    }
                ],
            }
        ),
    )

    ortholog = DB.Orthologs(
        ensembl=DEMO_ENSEMBL,
        Scientific_name="Mus musculus",
        ortholog_external_gene_name="Zfpdemo1",
        ortholog="ENSMUSGDEMO0001",
        homolog_perc_id="78.2",
        homolog_perc_id_r1="76.9",
        homolog_wga_coverage="88.5",
        homolog_orthology_confidence="1",
    )

    session.add_all([znf, repeat, repeat_family, chip_data, motif, cell_line, expression, gene_structure, ortholog])
    session.commit()


def main():
    parser = argparse.ArgumentParser(description="Seed a tiny demo dataset for the KRAB DB web app.")
    parser.add_argument("--refresh-demo", action="store_true", help="delete and recreate the demo rows")
    args = parser.parse_args()

    db, session = connect_db()
    create_demo_static_files()

    if demo_exists(session):
        if args.refresh_demo:
            clear_demo_data(session)
        else:
            print("demo data already exists; use --refresh-demo to recreate it")
            db.SessionDown()
            return

    seed_demo_data(session)
    db.SessionDown()
    print("demo data inserted")
    print("ZNF search term: ZNFDEMO1")
    print("Repeat search term: DEMO_REPEAT_A")
    print("ZNF detail URL: /KZFP/zinc_fingure/GSMDEMO001")


if __name__ == "__main__":
    main()
