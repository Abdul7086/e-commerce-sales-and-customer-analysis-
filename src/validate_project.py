"""Static end-to-end validation for the generated Superstore deliverables."""
from pathlib import Path
import json
import re
import sqlite3
import pandas as pd
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]

def require(ok, message):
    if not ok:
        raise AssertionError(message)
    print(f"PASS  {message}")

def main():
    processed = ROOT / "data" / "processed"
    clean = pd.read_csv(processed / "superstore_clean.csv")
    validation = json.loads((processed / "validation.json").read_text(encoding="utf-8"))
    require(len(clean) == 9994 and bool(clean["is_valid"].all()), "cleaned dataset has 9,994 valid rows")
    require(validation["row_id_unique"] and validation["ship_date_not_before_order"], "source validation checks pass")
    require(round(clean.sales.sum(), 2) == 2297200.65 and round(clean.profit.sum(), 2) == 286396.54, "sales and profit totals reconcile")

    wb = load_workbook(processed / "superstore_analysis.xlsx", read_only=True, data_only=True)
    require({"Clean Data", "Data Profile", "Year Category", "Region Segment"}.issubset(wb.sheetnames), "Excel workbook contains data, profiling, and analysis tabs")
    wb.close()
    with sqlite3.connect(processed / "superstore.db") as con:
        fact_rows = con.execute("SELECT COUNT(*) FROM fact_order_line").fetchone()[0]
        fk = con.execute("PRAGMA foreign_key_check").fetchall()
        require(fact_rows == 9994 and not fk, "SQLite model has 9,994 fact rows and no foreign-key violations")

    pbip = ROOT / "Superstore Sales Analysis.pbip"
    require(pbip.exists(), "Power BI project entry point is generated")
    pbip_obj = json.loads(pbip.read_text(encoding="utf-8"))
    report = ROOT / "Superstore Sales Analysis.Report"
    model = ROOT / "Superstore Sales Analysis.SemanticModel"
    require((report / "definition.pbir").exists() and (model / "definition.pbism").exists(), "PBIR report and TMDL semantic model folders are present")
    report_def = report / "definition"
    version = json.loads((report_def / "version.json").read_text(encoding="utf-8"))
    pages = json.loads((report_def / "pages" / "pages.json").read_text(encoding="utf-8"))
    require(version["version"] == "2.0.0", "PBIR content version is 2.0.0 for current Desktop")
    require(pages["$schema"].endswith("pagesMetadata/1.1.0/schema.json") and pages.get("activePageName") in pages["pageOrder"], "pages metadata uses current schema and activates a listed page")
    page_name = pages["activePageName"]
    page_dir = report_def / "pages" / page_name
    page = json.loads((page_dir / "page.json").read_text(encoding="utf-8"))
    visuals = list((page_dir / "visuals").glob("*/visual.json"))
    visual_data = [json.loads(p.read_text(encoding="utf-8")) for p in visuals]
    labels = {v.get("annotations", [{}])[0].get("value"): v for v in visual_data}
    require(page["width"] == 1280 and page["height"] == 720 and len(visual_data) == 14, "report has a 16:9 canvas and all 14 reference visuals")
    require(re.fullmatch(r"[0-9a-f]{20}", page["name"]) and page_dir.name == page["name"], "report page uses a Desktop-compatible object ID and matching folder")
    require(all(re.fullmatch(r"[0-9a-f]{20}", v["name"]) and p.parent.name == v["name"] for p, v in zip(visuals, visual_data)), "all visual folders use matching Desktop-compatible object IDs")
    require(sum(v["visual"]["visualType"] == "cardVisual" for v in visual_data) == 4, "report includes four current-format KPI cards")
    top_filter = labels["TopCustomers"]["filterConfig"]["filters"][0]
    top_query = top_filter["filter"]["From"][0]["Expression"]["Subquery"]["Query"]
    require(top_filter["type"] == "TopN" and top_query["Top"] == 10 and top_query["OrderBy"][0]["Direction"] == 2, "customer visual has a valid Top 10 by sales filter")
    report_platform = json.loads((report / ".platform").read_text(encoding="utf-8"))
    model_platform = json.loads((model / ".platform").read_text(encoding="utf-8"))
    require(report_platform["metadata"]["type"] == "Report" and model_platform["metadata"]["type"] == "SemanticModel", "report and semantic model include Fabric platform metadata")
    report_json = json.loads((report_def / "report.json").read_text(encoding="utf-8"))
    theme_item = report_json["resourcePackages"][0]["items"][0]
    theme_file = report / "StaticResources" / "RegisteredResources" / theme_item["path"]
    require(report_json["themeCollection"]["customTheme"]["name"] == "Superstore Executive" and theme_file.exists(), "report theme is registered and its resource file exists")

    table_dir = model / "definition" / "tables"
    table_text = {p.stem: p.read_text(encoding="utf-8") for p in table_dir.glob("*.tmdl")}
    require(set(table_text) == {"FactOrderLine", "DimCustomer", "DimProduct", "DimGeography", "DimShipMode", "DimDate"}, "TMDL model has the fact table and five dimensions")
    all_model = "\n".join(table_text.values())
    for table_name, definition in table_text.items():
        column_names = {m.group(1).strip().strip("'") for m in re.finditer(r"(?m)^\s*column\s+(.+?)\s*$", definition)}
        measure_names = {m.group(1).strip().strip("'") for m in re.finditer(r"(?m)^\s*measure\s+(.+?)\s*=", definition)}
        require(not (column_names & measure_names), f"{table_name} has no column/measure name conflicts")
    for v in visual_data:
        q = v["visual"].get("query", {}).get("queryState", {})
        for role in q.values():
            for p in role.get("projections", []):
                field = p["field"]
                if "Column" in field:
                    entity = field["Column"]["Expression"]["SourceRef"]["Entity"]
                    prop = field["Column"]["Property"]
                    require(entity in table_text and re.search(r"(?m)^\s*column\s+['\"]?" + re.escape(prop) + r"['\"]?\s*$", table_text[entity]), f"visual field exists: {entity}.{prop}")
                elif "Measure" in field:
                    entity = field["Measure"]["Expression"]["SourceRef"]["Entity"]
                    prop = field["Measure"]["Property"]
                    require(entity in table_text and re.search(r"(?m)^\s*measure\s+['\"]?" + re.escape(prop) + r"['\"]?\s*=", table_text[entity]), f"visual measure exists: {entity}.{prop}")
    expr = (model / "definition" / "expressions.tmdl").read_text(encoding="utf-8")
    require(str(ROOT) in expr and (processed / "superstore_clean.csv").exists(), "Power Query source resolves to this checkout's cleaned CSV")
    require(len(pbip_obj["artifacts"]) == 1 and pbip_obj["artifacts"][0]["report"]["path"] == report.name, "PBIP shortcut points at the generated report")
    print("All static end-to-end checks passed. Open and refresh the PBIP in Power BI Desktop for final application validation.")

if __name__ == "__main__":
    main()
