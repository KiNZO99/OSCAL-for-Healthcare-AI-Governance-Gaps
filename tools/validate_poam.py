# OSCAL POA&M Validator
# Validates POA&M JSON files against the OSCAL 1.1.2 schema
#
# Library repo: https://github.com/python-jsonschema/jsonschema
# Validation docs: https://python-jsonschema.readthedocs.io/en/stable/validate/
# OSCAL schema: https://github.com/usnistgov/OSCAL/releases/tag/v1.1.2

import json, sys, os
from jsonschema import Draft7Validator

def remove_unicode_patterns(obj):
    """Remove regex patterns using \\p{} syntax that Python cannot handle."""
    if isinstance(obj, dict):
        if "pattern" in obj and "\\p{" in obj["pattern"]:
            del obj["pattern"]
        for v in obj.values():
            remove_unicode_patterns(v)
    elif isinstance(obj, list):
        for v in obj:
            remove_unicode_patterns(v)

def validate(file_path):
    schema = json.load(open("schemas/oscal_poam_schema.json"))
    remove_unicode_patterns(schema)
    instance = json.load(open(file_path))
    name = os.path.basename(file_path)

    errors = list(Draft7Validator(schema).iter_errors(instance))
    if errors:
        print(f"FAIL: {name} ({len(errors)} errors)")
        for e in errors[:10]:
            print(f"  {e.message[:150]}")
        return

    poam = instance["plan-of-action-and-milestones"]
    print(f"PASS: {name}")
    print(f"  {len(poam.get('poam-items',[]))} poam-item(s), "
          f"{len(poam.get('risks',[]))} risk(s), "
          f"{len(poam.get('findings',[]))} finding(s), "
          f"{len(poam.get('observations',[]))} observation(s)")

    custom = []
    def scan(obj):
        if isinstance(obj, dict):
            if "ns" in obj and "name" in obj and "value" in obj:
                custom.append(f"{obj['name']}={obj['value']}")
            for v in obj.values(): scan(v)
        elif isinstance(obj, list):
            for v in obj: scan(v)
    scan(instance)
    print(f"  {len(custom)} custom property(s)")

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