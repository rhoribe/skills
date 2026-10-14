// Azure Bicep Topology
resource virtualNetwork 'Microsoft.Network/virtualNetworks@2023-04-01' = {
  name: 'my-vnet'
  location: 'eastus'
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
  }
}

resource subnetApp 'Microsoft.Network/virtualNetworks/subnets@2023-04-01' = {
  name: 'subnet-app'
  parent: virtualNetwork
  properties: {
    addressPrefix: '10.0.1.0/24'
  }
}

resource vmWeb 'Microsoft.Compute/virtualMachines@2023-03-01' = {
  name: 'vm-web-frontend'
  location: 'eastus'
  dependsOn: [
    virtualNetwork
  ]
}

resource sqlServer 'Microsoft.Sql/servers@2021-11-01' = {
  name: 'sql-db-server'
  location: 'eastus'
  dependsOn: [
    vmWeb
  ]
}

resource blobStorage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'mystorageaccount2026'
  location: 'eastus'
}
