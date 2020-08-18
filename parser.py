import csv
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
    node_data = pd.read_csv(node_file, sep="\t", usecols=[
        "id", "category", "publications", "sentence"])
    results = {}
    for rec in edge_data:
        _id = rec["subject"]
        edge_label = rec["edge_label"].replace("biolink:", "")
        object_name = rec["object"].split(":")[0].lower()
        association_type = rec["association_type"].replace("biolink:", "")
        subject_category = node_data.category[node_data.id == _id].squeeze()
        object_category = node_data.category[
                node_data.id == rec["object"]].squeeze()
        evidence = []
        if not pd.isna(rec["has_evidence"]):
            evidence_ids = rec["has_evidence"].split("|")
            for eid in evidence_ids:
                docs = node_data[node_data.id == eid].squeeze()
                evidence.append(
                        {"category": docs["category"].replace("biolink:", ""),
                         "sentence": docs["sentence"],
                         "pmc": docs["publications"].replace("PMCID:", "")
                         })
        data = {object_name: rec["object"],
                "category": object_category,
                "relation": rec["relation"],
                "association_type": association_type,
                "evidence": evidence}
        results.setdefault((_id, subject_category), {}).setdefault(
                edge_label, []).append(data)

    for (_id, category), edges in results.items():
        doc = {}
        doc["_id"] = _id
        doc["category"] = category
        for edge_label, docs in edges.items():
            doc[edge_label] = docs
        yield doc


if __name__ == "__main__":
    import json

    annotations = load_annotations("test-data/v0.1/")
    for a in annotations:
        print(json.dumps(a, indent=2))
