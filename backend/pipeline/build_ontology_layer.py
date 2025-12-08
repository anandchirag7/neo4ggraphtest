#!/usr/bin/env python3
"""
build_ontology_layer.py

Adds:
  - (IC) nodes
  - (Pin) nodes
  - (Constraint) nodes
  - (SpecItem) nodes (optional, from table CSVs)
  - Relationships:
      (Document)-[:HAS_IC]->(IC)
      (IC)-[:HAS_PIN]->(Pin)
      (Pin)-[:HAS_CONSTRAINT]->(Constraint)
      (Constraint)-[:DERIVED_FROM]->(Figure|Table|TextBlock|SpecItem)
      (Table)-[:HAS_SPEC_ITEM]->(SpecItem)
      (SpecItem)-[:APPLIES_TO_PIN]->(Pin)
      (Pin)-[:MENTIONED_IN]->(Figure|Table|TextBlock)
"""

import argparse
from pathlib import Path
from typing import Dict, Any, List

from neo4j import GraphDatabase

try:
    from pipeline.ontology_config import ONTOLOGY_CONFIG
except ModuleNotFoundError:
    from ontology_config import ONTOLOGY_CONFIG

try:
    import pandas as pd  # for SpecItem from CSV
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class OntologyBuilder:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # ---------- IC / Pin / Constraint creation ----------

    def create_ic_ontology(self, doc_id: str):
        config = ONTOLOGY_CONFIG.get(doc_id)
        if not config:
            print(f"[WARN] No ontology config for doc_id={doc_id}")
            return

        with self.driver.session() as session:
            for ic_cfg in config.get("ics", []):
                ic_name = ic_cfg["name"]

                # IC node and link to Document
                session.run(
                    """
                    MATCH (d:Document {doc_id: $doc_id})
                    MERGE (ic:IC {name: $ic_name, doc_id: $doc_id})
                    MERGE (d)-[:HAS_IC]->(ic)
                    """,
                    doc_id=doc_id,
                    ic_name=ic_name,
                )

                # Pins
                for pin_name in ic_cfg.get("pins", []):
                    session.run(
                        """
                        MATCH (ic:IC {name: $ic_name, doc_id: $doc_id})
                        MERGE (p:Pin {name: $pin_name, ic_name: $ic_name, doc_id: $doc_id})
                        MERGE (ic)-[:HAS_PIN]->(p)
                        """,
                        doc_id=doc_id,
                        ic_name=ic_name,
                        pin_name=pin_name,
                    )

                # Constraints
                for c in ic_cfg.get("constraints", []):
                    self._create_constraint(session, doc_id, ic_name, c)

                # Optional: create Pin↔content MENTIONED_IN links via text search
                self._link_pins_to_content(session, doc_id, ic_name, ic_cfg.get("pins", []))

    def _create_constraint(self, session, doc_id: str, ic_name: str, c: Dict[str, Any]):
        cid = c["id"]
        pin_name = c["pin"]
        description = c.get("description")
        ctype = c.get("type")
        value = c.get("value")
        unit = c.get("unit")
        keywords = c.get("keywords", [])

        # Constraint node + Pin->Constraint relation
        session.run(
            """
            MATCH (p:Pin {name: $pin_name, ic_name: $ic_name, doc_id: $doc_id})
            MERGE (c:Constraint {id: $cid, doc_id: $doc_id})
            SET c.type = $ctype,
                c.value = $value,
                c.unit = $unit,
                c.description = $description
            MERGE (p)-[:HAS_CONSTRAINT]->(c)
            """,
            doc_id=doc_id,
            ic_name=ic_name,
            pin_name=pin_name,
            cid=cid,
            ctype=ctype,
            value=value,
            unit=unit,
            description=description,
        )

        # Try to link constraint to relevant Tables / TextBlocks / Figures
        if keywords:
            self._link_constraint_to_sources(session, doc_id, cid, keywords)

    def _link_constraint_to_sources(self, session, doc_id: str, cid: str, keywords: List[str]):
        """
        Simple heuristic:
        - find any TextBlock/Figure/Table whose text contains ALL keywords
        - connect (Constraint)-[:DERIVED_FROM]->(that node)
        """
        kw_l = [k.lower() for k in keywords if k]

        def _where_clause(var: str) -> str:
            return " AND ".join([f"toLower({var}.natural_language_context) CONTAINS '{k}'" for k in kw_l])

        # Figures
        if kw_l:
            session.run(
                f"""
                MATCH (c:Constraint {{id: $cid, doc_id: $doc_id}})
                MATCH (p:Page {{doc_id: $doc_id}})-[:HAS_FIGURE]->(f:Figure)
                WHERE {_where_clause('f')}
                MERGE (c)-[:DERIVED_FROM]->(f)
                """,
                doc_id=doc_id,
                cid=cid,
            )
            # Tables
            session.run(
                f"""
                MATCH (c:Constraint {{id: $cid, doc_id: $doc_id}})
                MATCH (p:Page {{doc_id: $doc_id}})-[:HAS_TABLE]->(t:Table)
                WHERE {_where_clause('t')}
                MERGE (c)-[:DERIVED_FROM]->(t)
                """,
                doc_id=doc_id,
                cid=cid,
            )
            # TextBlocks
            session.run(
                f"""
                MATCH (c:Constraint {{id: $cid, doc_id: $doc_id}})
                MATCH (p:Page {{doc_id: $doc_id}})-[:HAS_TEXT_BLOCK]->(tb:TextBlock)
                WHERE {_where_clause('tb')}
                MERGE (c)-[:DERIVED_FROM]->(tb)
                """,
                doc_id=doc_id,
                cid=cid,
            )

    # ---------- Pin↔content MENTIONED_IN ----------

    def _link_pins_to_content(self, session, doc_id: str, ic_name: str, pins: List[str]):
        """
        For each Pin name, find any TextBlock/Figure/Table containing that token and
        connect (Pin)-[:MENTIONED_IN]->(node).
        """
        for pin_name in pins:
            token = pin_name  # simple; you can add regex if needed

            # TextBlocks
            session.run(
                """
                MATCH (p:Pin {name: $pin_name, ic_name: $ic_name, doc_id: $doc_id})
                MATCH (pg:Page {doc_id: $doc_id})-[:HAS_TEXT_BLOCK]->(tb:TextBlock)
                WHERE tb.summary CONTAINS $token OR tb.summary CONTAINS $token + ' '
                MERGE (p)-[:MENTIONED_IN]->(tb)
                """,
                doc_id=doc_id,
                ic_name=ic_name,
                pin_name=pin_name,
                token=token,
            )

            # Figures
            session.run(
                """
                MATCH (p:Pin {name: $pin_name, ic_name: $ic_name, doc_id: $doc_id})
                MATCH (pg:Page {doc_id: $doc_id})-[:HAS_FIGURE]->(f:Figure)
                WHERE f.natural_language_context CONTAINS $token
                MERGE (p)-[:MENTIONED_IN]->(f)
                """,
                doc_id=doc_id,
                ic_name=ic_name,
                pin_name=pin_name,
                token=token,
            )

            # Tables
            session.run(
                """
                MATCH (p:Pin {name: $pin_name, ic_name: $ic_name, doc_id: $doc_id})
                MATCH (pg:Page {doc_id: $doc_id})-[:HAS_TABLE]->(t:Table)
                WHERE t.natural_language_context CONTAINS $token
                MERGE (p)-[:MENTIONED_IN]->(t)
                """,
                doc_id=doc_id,
                ic_name=ic_name,
                pin_name=pin_name,
                token=token,
            )

    # ---------- Optional: SpecItem from table CSV ----------

    def create_spec_items_from_tables(self, doc_id: str):
        """
        For each Table node that has path set to a CSV:
          - read the CSV
          - create SpecItem rows
          - link them to Table
          - heuristically link to Pins based on pin names present in the row
        """
        if not HAS_PANDAS:
            print("[INFO] pandas not installed; skipping SpecItem creation.")
            return

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (t:Table {doc_id: $doc_id})
                WHERE t.path IS NOT NULL
                RETURN t.table_id AS table_id, t.path AS path
                """,
                doc_id=doc_id,
            )
            for record in result:
                table_id = record["table_id"]
                path = record["path"]
                if not path:
                    continue
                self._create_spec_items_for_table(session, doc_id, table_id, path)

    def _create_spec_items_for_table(self, session, doc_id: str, table_id: str, path: str):
        try:
            df = pd.read_csv(path)
        except Exception as e:
            print(f"[WARN] Could not read table CSV {path}: {e}")
            return

        df = df.fillna("")

        for idx, row in df.iterrows():
            spec_id = f"{table_id}_row{idx+1}"
            row_text = " | ".join(str(v) for v in row.values)

            session.run(
                """
                MATCH (t:Table {table_id: $table_id, doc_id: $doc_id})
                MERGE (s:SpecItem {id: $spec_id, doc_id: $doc_id})
                SET s.row_index = $row_index,
                    s.raw_text = $row_text
                MERGE (t)-[:HAS_SPEC_ITEM]->(s)
                """,
                doc_id=doc_id,
                table_id=table_id,
                spec_id=spec_id,
                row_index=int(idx),
                row_text=row_text,
            )

            # Try to link SpecItem to Pins if pin names appear in the row
            session.run(
                """
                MATCH (s:SpecItem {id: $spec_id, doc_id: $doc_id})
                MATCH (p:Pin {doc_id: $doc_id})
                WHERE s.raw_text CONTAINS p.name
                MERGE (s)-[:APPLIES_TO_PIN]->(p)
                """,
                doc_id=doc_id,
                spec_id=spec_id,
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--neo4j_uri", required=True)
    parser.add_argument("--neo4j_user", required=True)
    parser.add_argument("--neo4j_password", required=True)
    parser.add_argument("--doc_id", required=True, help="doc_id to build ontology for (e.g. RT6220_DS-12)")
    parser.add_argument("--with_spec_items", action="store_true", help="Also create SpecItem nodes from table CSV")

    args = parser.parse_args()

    builder = OntologyBuilder(args.neo4j_uri, args.neo4j_user, args.neo4j_password)
    try:
        print(f"[OK] Creating IC / Pin / Constraint ontology for doc_id={args.doc_id}")
        builder.create_ic_ontology(args.doc_id)

        if args.with_spec_items:
            print("[OK] Creating SpecItem nodes from tables")
            builder.create_spec_items_from_tables(args.doc_id)
    finally:
        builder.close()


if __name__ == "__main__":
    main()
