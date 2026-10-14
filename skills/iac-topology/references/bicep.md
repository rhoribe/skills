# Azure Bicep & ARM Topology Guide

This reference guide describes how `iac-topology` parses Microsoft Azure Bicep files (`.bicep`) and Azure Resource Manager (ARM) JSON templates.

---

## 1. Bicep Syntax & Resource Representation

Bicep uses declarative symbolic identifiers:

```bicep
resource vnet 'Microsoft.Network/virtualNetworks@2023-04-01' = {
  name: 'prod-vnet'
  ...
}

resource subnet 'Microsoft.Network/virtualNetworks/subnets@2023-04-01' = {
  parent: vnet
  name: 'app-subnet'
  ...
}
```

The parser detects:
- **Symbolic Name**: e.g., `vnet`, `subnet`.
- **Resource Type**: e.g., `Microsoft.Network/virtualNetworks`.
- **API Version**: e.g., `@2023-04-01`.
- **Parent-Child Hierarchy**: `parent: vnet` nests the subnet inside the virtual network container.
- **Modules**: `module myMod './modules/app.bicep' = { ... }` renders as modular container nodes.

---

## 2. Dependency Extraction

Dependencies in Bicep are inferred from:
1. **Direct Property Referencing**: Accessing properties like `vnet.id` or `nic.properties.ipConfigurations` establishes an edge from the consumer to the target resource.
2. **Parent Hierarchies**: `parent: <identifier>` establishes structural nesting and connectivity.
3. **Explicit `dependsOn` Blocks**: `dependsOn: [ storageAccount, keyVault ]`.

---

## 3. ARM Template Compatibility

Standard ARM templates (`$schema: .../deploymentTemplate.json#`) are parsed directly via JSON ingestion, extracting resources, types, and dependencies.
