import csv
import json
import os
import re

import pandas as pd


def load_annotations(data_folder):
    # Assuming that future releases will keep the same file naming pattern
    files = [f for f in os.listdir(data_folder)]
    node_file = os.path.join(data_folder, [f for f in files if re.match(
                    "^sample-craft-nodes\.v.*\.kgx\.tsv$", f)][-1]
                    )
    edge_file = os.path.join(data_folder, [f for f in files if re.match(
                    "^sample-craft-edges\.v.*\.kgx\.tsv$", f)][-1]
                    )
    edge_data = pd.read_csv(edge_file, sep="\t", quoting=csv.QUOTE_NONE)\
        .to_dict(orient='records')
    node_data = pd.read_csv(node_file, sep="\t",
                            usecols=["id", "publications", "sentence"])
    results = {}
    for rec in edge_data:
        _id = rec["subject"]
        edge_label = rec["edge_label"].replace("biolink:", "")
        object_name = rec["object"].split(":")[0].lower()
        association_type = rec["association_type"].replace("biolink:", "")
        evidence = []
        if not pd.isna(rec["has_evidence"]):
            evidence_ids = rec["has_evidence"].split("|")
            for eid in evidence_ids:
                docs = node_data[node_data["id"] == eid].squeeze()
                evidence.append({"sentence": docs["sentence"],
                                 "pmc": docs["publications"].replace(
                                     "PMCID:", "")
                                 })
        data = {object_name: rec["object"],
                "relation": rec["relation"],
                "association_type": association_type,
                "evidence": evidence}
        results.setdefault((_id, edge_label), []).append(data)

    for (_id, edge_label), docs in results.items():
        doc = {"_id": _id, edge_label: docs}
        print(json.dumps(doc, indent=2))
        #yield doc


if __name__ == "__main__":
    load_annotations("test-data")
