# AWS CloudFormation Topology Guide

This reference guide details how `iac-topology` parses AWS CloudFormation YAML and JSON templates, resolves intrinsic functions, and extracts multi-tier architectures.

---

## 1. Supported Formats & Template Features

`iac-topology` parses both JSON and YAML CloudFormation templates:
- Supports YAML short syntax (`!Ref`, `!GetAtt`, `!Sub`, `!ImportValue`) as well as standard mapping syntax (`{"Ref": "..."}`).
- Evaluates top-level `Resources` mappings.
- Resolves container groupings for VPCs, Subnets, and ECS/EKS clusters.

---

## 2. Intrinsic Function Resolution

The parser inspects template properties to generate directional relationship arrows:

| Intrinsic Function | Syntax | Inferred Edge Type |
|---|---|---|
| `Ref` | `!Ref DatabaseSubnet` | Reference / Dependency |
| `Fn::GetAtt` | `!GetAtt MyEC2Instance.PublicIp` | Attribute Consumer |
| `DependsOn` | `DependsOn: [MyVPC, AppSecurityGroup]` | Explicit Precedence |
| `Fn::Sub` | `!Sub "${WebServer}.internal"` | Interpolated Reference |

---

## 3. Standard AWS 3-Tier Mapping

When visualizing a multi-tier AWS architecture:
1. **Edge Tier**: `AWS::ElasticLoadBalancingV2::LoadBalancer`, `AWS::ApiGateway::RestApi`, `AWS::CloudFront::Distribution`.
2. **Compute Tier**: `AWS::EC2::Instance`, `AWS::ECS::Service`, `AWS::Lambda::Function`.
3. **Data Tier**: `AWS::RDS::DBInstance`, `AWS::DynamoDB::Table`, `AWS::ElastiCache::ReplicationGroup`.
4. **Storage Tier**: `AWS::S3::Bucket`, `AWS::EFS::FileSystem`.
5. **Security & Governance**: `AWS::IAM::Role`, `AWS::KMS::Key`, `AWS::EC2::SecurityGroup`.
