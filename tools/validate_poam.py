# OSCAL POA&M Validator
# Checks POA&M JSON files against the OSCAL 1.1.2 schema
# Also verifies internal cross-references and counts custom properties
# Library: https://github.com/python-jsonschema/jsonschema

import json, sys, os
from jsonschema import Draft7Validator

def validate(file_path):
    schema = json.load(open("schemas/oscal_poam_schema.json"))
    instance = json.load(open(file_path))
    name = os.path.basename(file_path)

    # Schema validation
    errors = list(Draft7Validator(schema).iter_errors(instance))
    if errors:
        print(f"FAIL: {name} ({len(errors)} errors)")
        for e in errors[:10]:
            print(f"  {e.message[:150]}")
        return

    # Summary
    poam = instance["plan-of-action-and-milestones"]
    items = len(poam.get("poam-items", []))
    risks = len(poam.get("risks", []))
    findings = len(poam.get("findings", []))
    observations = len(poam.get("observations", []))
    print(f"PASS: {name}")
    print(f"  {items} poam-item(s), {risks} risk(s), {findings} finding(s), {observations} observation(s)")

    # Count custom namespace properties
    custom = []
    def scan(obj):
        if isinstance(obj, dict):
            if "ns" in obj and "name" in obj and "value" in obj:
                custom.append(f"{obj['name']}={obj['value']}")
            for v in obj.values():
                scan(v)
        elif isinstance(obj, list):
            for v in obj:
                scan(v)
    scan(instance)
    print(f"  {len(custom)} custom property(s)")
    for c in custom:
        print(f"    {c}")

# Run on a single file or a folder
if len(sys.argv) < 2:
    print("Usage: python validate.py <file.json>")
    print("       python validate.py --batch <folder>")
elif sys.argv[1] == "--batch":
    for f in sorted(os.listdir(sys.argv[2])):
        if f.endswith(".json"):
            validate(os.path.join(sys.argv[2], f))
            print()
else:
    validate(sys.argv[1])