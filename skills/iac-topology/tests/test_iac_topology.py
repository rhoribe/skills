#!/usr/bin/env python3
"""
Unit and integration tests for iac-topology parser and generators.
Verifies parsing accuracy and output validity for:
- Terraform
- CloudFormation
- Azure Bicep
- Ansible
- Excalidraw JSON schema
- Draw.io XML schema
- Mermaid flowchart syntax
"""

import os
import sys
import json
import subprocess
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
FIXTURES_DIR = BASE_DIR / "tests" / "fixtures"

sys.path.insert(0, str(SCRIPTS_DIR))
from parse_iac import IaCParser
from generate_excalidraw import ExcalidrawGenerator
from generate_drawio import DrawioGenerator
from generate_mermaid import MermaidGenerator


class TestIaCTopology(unittest.TestCase):

    def test_terraform_parsing(self):
        tf_file = FIXTURES_DIR / "aws_vpc.tf"
        parser = IaCParser()
        parser.ingest_file(str(tf_file))
        ir = parser.to_dict()

        self.assertEqual(ir["source_type"], "terraform")
        self.assertGreaterEqual(ir["summary"]["total_nodes"], 5)
        # Check specific nodes
        node_ids = [n["id"] for n in ir["nodes"]]
        self.assertIn("aws_instance.web", node_ids)
        self.assertIn("aws_db_instance.db", node_ids)
        self.assertIn("aws_s3_bucket.assets", node_ids)

        # Check groups
        group_ids = [g["id"] for g in ir["groups"]]
        self.assertTrue(any("vpc" in gid for gid in group_ids))

        # Check edges
        self.assertGreaterEqual(len(ir["edges"]), 1)

    def test_cloudformation_parsing(self):
        cfn_file = FIXTURES_DIR / "cloudformation.yaml"
        parser = IaCParser()
        parser.ingest_file(str(cfn_file))
        ir = parser.to_dict()

        self.assertEqual(ir["source_type"], "cloudformation")
        node_ids = [n["id"] for n in ir["nodes"]]
        self.assertIn("MyVPC", node_ids)
        self.assertIn("WebServer", node_ids)
        self.assertIn("DatabaseInstance", node_ids)
        self.assertIn("StaticStorage", node_ids)

        # Check edges (DependsOn or Ref)
        self.assertGreaterEqual(len(ir["edges"]), 1)

    def test_bicep_parsing(self):
        bicep_file = FIXTURES_DIR / "azure_app.bicep"
        parser = IaCParser()
        parser.ingest_file(str(bicep_file))
        ir = parser.to_dict()

        self.assertEqual(ir["source_type"], "bicep")
        node_ids = [n["id"] for n in ir["nodes"]]
        self.assertIn("virtualNetwork", node_ids)
        self.assertIn("subnetApp", node_ids)
        self.assertIn("vmWeb", node_ids)
        self.assertIn("sqlServer", node_ids)
        self.assertIn("blobStorage", node_ids)

        # Check dependsOn edge
        edges = [(e["source"], e["target"]) for e in ir["edges"]]
        self.assertIn(("vmWeb", "virtualNetwork"), edges)

    def test_ansible_parsing(self):
        ansible_file = FIXTURES_DIR / "playbook.yml"
        parser = IaCParser()
        parser.ingest_file(str(ansible_file))
        ir = parser.to_dict()

        self.assertEqual(ir["source_type"], "ansible")
        self.assertGreaterEqual(ir["summary"]["total_nodes"], 4)
        node_names = [n["name"] for n in ir["nodes"]]
        self.assertIn("web-app-node", node_names)
        self.assertIn("ansible-backup-vault", node_names)

    def test_excalidraw_generation(self):
        tf_file = FIXTURES_DIR / "aws_vpc.tf"
        parser = IaCParser()
        parser.ingest_file(str(tf_file))
        ir = parser.to_dict()

        gen = ExcalidrawGenerator(ir)
        excal = gen.generate()

        self.assertEqual(excal["type"], "excalidraw")
        self.assertEqual(excal["version"], 2)
        self.assertIn("elements", excal)
        self.assertGreater(len(excal["elements"]), 0)

        # Ensure elements have required fields
        element_types = set()
        for el in excal["elements"]:
            self.assertIn("id", el)
            self.assertIn("type", el)
            self.assertIn("x", el)
            self.assertIn("y", el)
            element_types.add(el["type"])

        self.assertIn("rectangle", element_types)
        self.assertIn("text", element_types)

    def test_drawio_generation(self):
        tf_file = FIXTURES_DIR / "aws_vpc.tf"
        parser = IaCParser()
        parser.ingest_file(str(tf_file))
        ir = parser.to_dict()

        gen = DrawioGenerator(ir)
        drawio_xml = gen.generate()

        # Check XML parses with standard ElementTree
        root = ET.fromstring(drawio_xml)
        self.assertEqual(root.tag, "mxfile")
        diagram = root.find("diagram")
        self.assertIsNotNone(diagram)
        model = diagram.find("mxGraphModel")
        self.assertIsNotNone(model)
        cells = model.find("root").findall("mxCell")
        self.assertGreater(len(cells), 5)

    def test_mermaid_generation(self):
        tf_file = FIXTURES_DIR / "aws_vpc.tf"
        parser = IaCParser()
        parser.ingest_file(str(tf_file))
        ir = parser.to_dict()

        gen = MermaidGenerator(ir)
        mmd = gen.generate()

        self.assertTrue(mmd.startswith("flowchart TD"))
        self.assertIn("subgraph", mmd)
        self.assertIn("classDef", mmd)

    def test_end_to_end_cli(self):
        out_dir = BASE_DIR / "tests" / "output_test"
        cli = SCRIPTS_DIR / "iac_topology.sh"
        cmd = [
            str(cli),
            str(FIXTURES_DIR / "aws_vpc.tf"),
            "-o", str(out_dir),
            "-f", "all"
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0, f"CLI error: {res.stderr}")
        self.assertTrue((out_dir / "aws_vpc.excalidraw").is_file())
        self.assertTrue((out_dir / "aws_vpc.drawio").is_file())
        self.assertTrue((out_dir / "aws_vpc.mmd").is_file())


if __name__ == "__main__":
    unittest.main()
