"""Export the three consolidated PlantUML class diagrams as UML 2.1 XMI."""
from pathlib import Path
import re
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
XMI = "http://schema.omg.org/spec/XMI/2.1"
UML = "http://www.eclipse.org/uml2/2.1.0/UML"
ET.register_namespace("xmi", XMI)
ET.register_namespace("uml", UML)

def xid(value):
    return "id_" + uuid.uuid5(uuid.NAMESPACE_URL, "erasmus-p1:" + value).hex

sources = [ROOT / f"docs/diagrams/fig{n}-final-structural-{name}.puml" for n, name in
           [(16, "learning-agreement"), (17, "equivalence"), (18, "mobility-preparation")]]
model = ET.Element(f"{{{XMI}}}XMI", {f"{{{XMI}}}version": "2.1"})
uml = ET.SubElement(model, f"{{{UML}}}Model", {f"{{{XMI}}}id": xid("model"), "name": "ErasmusModel"})
contexts = {}
types = {}
members = []
relations = []
for source in sources:
    package = None
    element = None
    for raw in source.read_text().splitlines():
        line = raw.strip()
        match = re.match(r'package "ro\.uaic\.feaa\.erasmus\.([^.]+)\.([^"]+)" \{', line)
        if match:
            context, layer = match.groups()
            if context not in contexts:
                contexts[context] = ET.SubElement(uml, "packagedElement", {f"{{{XMI}}}type": "uml:Package", f"{{{XMI}}}id": xid("package:" + context), "name": context})
            package = ET.SubElement(contexts[context], "packagedElement", {f"{{{XMI}}}type": "uml:Package", f"{{{XMI}}}id": xid("package:" + context + "." + layer), "name": layer})
            continue
        match = re.match(r'(class|interface|enum|abstract class) (\w+)(?: <<[^>]+>>)? \{', line)
        if match and package is not None:
            kind, name = match.groups()
            qualified = context + "." + layer + "." + name
            umlkind = "Enumeration" if kind == "enum" else "Interface" if kind == "interface" else "Class"
            attrs = {f"{{{XMI}}}type": "uml:" + umlkind, f"{{{XMI}}}id": xid("type:" + qualified), "name": name}
            if kind == "abstract class": attrs["isAbstract"] = "true"
            element = ET.SubElement(package, "packagedElement", attrs)
            types[qualified] = element
            continue
        if element is not None:
            if line == "}":
                element = None
                continue
            if line.startswith(("+", "-", "#")):
                members.append((element, context, layer, line))
            elif element.attrib.get(f"{{{XMI}}}type") == "uml:Enumeration" and re.fullmatch(r"[A-Z][A-Z_]+", line):
                ET.SubElement(element, "ownedLiteral", {f"{{{XMI}}}id": xid("literal:" + element.attrib["name"] + "." + line), "name": line})
            continue
        if line.startswith("'") or not line or line.startswith("@"):
            continue
        match = re.match(r'(\w+)\s+(\*--|\.\.\|>|--\|>|-->|\.\.>)\s+(?:"([^"]+)"\s+)?(\w+)', line)
        if match:
            relations.append((context, *match.groups()))

def resolve(name, context, layer):
    name = re.sub(r"<.*", "", name).strip()
    local = context + "." + layer + "." + name
    if local in types: return types[local].attrib[f"{{{XMI}}}id"]
    candidates = [v for k, v in types.items() if k.endswith("." + name)]
    if len(candidates) == 1: return candidates[0].attrib[f"{{{XMI}}}id"]
    return None

for owner, context, layer, line in members:
    visibility = {"+": "public", "-": "private", "#": "protected"}[line[0]]
    body = line[1:].strip()
    method = re.match(r'(\w+)\((.*?)\):\s*(.+)', body)
    if method:
        name, args, result = method.groups()
        op = ET.SubElement(owner, "ownedOperation", {f"{{{XMI}}}id": xid(owner.attrib[f"{{{XMI}}}id"] + ":op:" + name), "name": name, "visibility": visibility})
        for arg in [a.strip() for a in args.split(",") if a.strip()]:
            m = re.match(r'(\w+):\s*(.+)', arg)
            if m:
                pname, ptype = m.groups()
                attrs = {f"{{{XMI}}}id": xid(op.attrib[f"{{{XMI}}}id"] + ":" + pname), "name": pname}
                ref = resolve(ptype, context, layer)
                if ref: attrs["type"] = ref
                param = ET.SubElement(op, "ownedParameter", attrs)
                if not ref: ET.SubElement(param, "type", {f"{{{XMI}}}type": "uml:PrimitiveType", "href": "pathmap://UML_LIBRARIES/UMLPrimitiveTypes.library.uml#" + ptype})
        if result != "void":
            attrs = {f"{{{XMI}}}id": xid(op.attrib[f"{{{XMI}}}id"] + ":return"), "direction": "return"}
            ref = resolve(result, context, layer)
            if ref: attrs["type"] = ref
            param = ET.SubElement(op, "ownedParameter", attrs)
            if not ref: ET.SubElement(param, "type", {f"{{{XMI}}}type": "uml:PrimitiveType", "href": "pathmap://UML_LIBRARIES/UMLPrimitiveTypes.library.uml#" + result})
    else:
        m = re.match(r'(\w+):\s*(.+)', body)
        if not m: continue
        name, typename = m.groups()
        attrs = {f"{{{XMI}}}id": xid(owner.attrib[f"{{{XMI}}}id"] + ":attr:" + name), "name": name, "visibility": visibility}
        ref = resolve(typename, context, layer)
        if ref: attrs["type"] = ref
        prop = ET.SubElement(owner, "ownedAttribute", attrs)
        if not ref: ET.SubElement(prop, "type", {f"{{{XMI}}}type": "uml:PrimitiveType", "href": "pathmap://UML_LIBRARIES/UMLPrimitiveTypes.library.uml#" + typename})

for context, source, kind, multiplicity, target in relations:
    source_id = resolve(source, context, "domain") or next((v.attrib[f"{{{XMI}}}id"] for k, v in types.items() if k.startswith(context + ".") and k.endswith("." + source)), None)
    target_id = resolve(target, context, "domain") or next((v.attrib[f"{{{XMI}}}id"] for k, v in types.items() if k.startswith(context + ".") and k.endswith("." + target)), None)
    if not source_id or not target_id: continue
    rid = xid("relation:" + context + ":" + source + ":" + kind + ":" + target)
    if kind in ("--|>", "..|>"):
        owner = next(v for v in types.values() if v.attrib[f"{{{XMI}}}id"] == source_id)
        tag = "interfaceRealization" if kind == "..|>" else "generalization"
        ET.SubElement(owner, tag, {f"{{{XMI}}}id": rid, "supplier" if tag == "interfaceRealization" else "general": target_id, **({"client": source_id} if tag == "interfaceRealization" else {})})
    elif kind == "*--":
        association = ET.SubElement(uml, "packagedElement", {f"{{{XMI}}}type": "uml:Association", f"{{{XMI}}}id": rid, "name": source + "_" + target})
        for index, (tid, aggregate) in enumerate(((source_id, "composite"), (target_id, "none"))):
            end = ET.SubElement(association, "ownedEnd", {f"{{{XMI}}}id": xid(rid + str(index)), "type": tid, "aggregation": aggregate})
            if index == 1 and multiplicity:
                ET.SubElement(end, "lowerValue", {f"{{{XMI}}}type": "uml:LiteralInteger", f"{{{XMI}}}id": xid(rid + "lower"), "value": multiplicity.split("..")[0]})
                ET.SubElement(end, "upperValue", {f"{{{XMI}}}type": "uml:LiteralUnlimitedNatural", f"{{{XMI}}}id": xid(rid + "upper"), "value": multiplicity.split("..")[-1]})
    else:
        ET.SubElement(uml, "packagedElement", {f"{{{XMI}}}type": "uml:Dependency", f"{{{XMI}}}id": rid, "name": source + "_uses_" + target, "client": source_id, "supplier": target_id})

output = ROOT / "models/xmi-exports/ErasmusModel.xmi"
ET.indent(model, space="  ")
ET.ElementTree(model).write(output, encoding="utf-8", xml_declaration=True)
print(f"Exported {len(types)} types and {len(relations)} relationships to {output}")
