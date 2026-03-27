# Chapter 44: Cloud Deployment - Modern Infrastructure and Scalability

## 🎯 Learning Objectives

By the end of this chapter, you will master:
- **Deploying** ERPNext on major cloud platforms (AWS, Azure, GCP)
- **Implementing** containerized deployments with Docker and Kubernetes
- **Setting up** auto-scaling and load balancing for high availability
- **Configuring** cloud-native services and managed databases
- **Implementing** CI/CD pipelines for cloud deployment
- **Managing** cloud costs and resource optimization
- **Securing** cloud deployments with best practices
- **Monitoring** and maintaining cloud-based ERPNext applications

## 📚 Chapter Topics

### 44.1 Cloud Platform Overview

**Understanding Cloud Deployment Options**

Cloud deployment offers scalability, reliability, and managed services that traditional hosting cannot provide. Understanding the options helps choose the right platform.

> **📊 Visual Reference**: See ERPNext architecture diagram in `resources/diagrams/erpnext_architecture.md` for understanding how cloud deployment fits into overall system architecture.

#### Cloud Platform Comparison

```python
# Cloud platform comparison for ERPNext
class CloudPlatformComparison:
    """Comparison of major cloud platforms for ERPNext deployment"""
    
    PLATFORMS = {
        'aws': {
            'name': 'Amazon Web Services',
            'strengths': ['Mature ecosystem', 'Wide service variety', 'Good documentation', 'Cost-effective'],
            'weaknesses': ['Complex pricing', 'Learning curve', 'Vendor lock-in risk'],
            'best_for': ['Enterprise', 'Scalable applications', 'Global deployment'],
            'key_services': ['EC2', 'RDS', 'S3', 'ElasticLoadBalancer', 'ECS/EKS', 'CloudFormation']
        },
        'azure': {
            'name': 'Microsoft Azure',
            'strengths': ['Enterprise integration', 'Hybrid cloud support', 'Good Windows support', 'Azure AD integration'],
            'weaknesses': ['Less mature than AWS', 'Higher costs', 'Complex portal'],
            'best_for': ['Microsoft shops', 'Enterprise with Microsoft stack', 'Hybrid deployments'],
            'key_services': ['VMs', 'Azure SQL', 'Blob Storage', 'Load Balancer', 'AKS', 'Resource Manager']
        },
        'gcp': {
            'name': 'Google Cloud Platform',
            'strengths': ['Strong ML/AI', 'Good pricing', 'Excellent networking', 'Kubernetes expertise'],
            'weaknesses': ['Smaller ecosystem', 'Less enterprise features', 'Documentation gaps'],
            'best_for': ['Data-intensive apps', 'ML-enabled features', 'Global applications'],
            'key_services': ['Compute Engine', 'Cloud SQL', 'Cloud Storage', 'Load Balancing', 'GKE', 'Deployment Manager']
        },
        'digitalocean': {
            'name': 'DigitalOcean',
            'strengths': ['Simple pricing', 'Good documentation', 'Developer-friendly', 'Fast SSD storage'],
            'weaknesses': ['Limited enterprise features', 'Smaller global presence', 'Fewer managed services'],
            'best_for': ['Startups', 'SMBs', 'Simple deployments', 'Cost-sensitive projects'],
            'key_services': ['Droplets', 'Managed Databases', 'Spaces', 'Load Balancers', 'Kubernetes']
        }
    }
    
    def recommend_platform(self, requirements):
        """Recommend best cloud platform based on requirements"""
        
        scores = {}
        
        for platform, config in self.PLATFORMS.items():
            score = 0
            
            # Size requirement
            if requirements.get('size') == 'enterprise':
                if platform in ['aws', 'azure']:
                    score += 3
                elif platform == 'gcp':
                    score += 2
                else:
                    score += 1
            elif requirements.get('size') == 'startup':
                if platform == 'digitalocean':
                    score += 3
                elif platform in ['aws', 'gcp']:
                    score += 2
                else:
                    score += 1
            
            # Microsoft stack requirement
            if requirements.get('microsoft_stack'):
                if platform == 'azure':
                    score += 3
                else:
                    score += 0
            
            # Cost sensitivity
            if requirements.get('cost_sensitive'):
                if platform in ['digitalocean', 'gcp']:
                    score += 2
                elif platform == 'aws':
                    score += 1
                else:
                    score += 0
            
            # Global presence
            if requirements.get('global_presence'):
                if platform in ['aws', 'azure', 'gcp']:
                    score += 2
                else:
                    score += 1
            
            scores[platform] = score
        
        # Return recommendation
        recommended = max(scores, key=scores.get)
        return {
            'platform': recommended,
            'reasoning': f"Highest score ({scores[recommended]}) based on requirements",
            'all_scores': scores
        }
```

### 44.2 AWS Deployment

**Deploying ERPNext on Amazon Web Services**

```python
# AWS deployment configuration
class AWSDeployment:
    """Comprehensive AWS deployment for ERPNext"""
    
    def __init__(self):
        self.region = 'us-east-1'
        self.vpc_config = self._setup_vpc()
        self.security_config = self._setup_security()
        self.storage_config = self._setup_storage()
        self.compute_config = self._setup_compute()
        self.database_config = self._setup_database()
        self.networking_config = self._setup_networking()
    
    def create_cloudformation_template(self):
        """Create CloudFormation template for ERPNext deployment"""
        
        template = {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Description': 'ERPNext deployment on AWS',
            'Parameters': {
                'EnvironmentName': {
                    'Type': 'String',
                    'Default': 'production',
                    'Description': 'Environment name'
                },
                'InstanceType': {
                    'Type': 'String',
                    'Default': 't3.medium',
                    'AllowedValues': ['t3.micro', 't3.small', 't3.medium', 't3.large', 'm5.large', 'm5.xlarge'],
                    'Description': 'EC2 instance type'
                },
                'DBInstanceClass': {
                    'Type': 'String',
                    'Default': 'db.t3.medium',
                    'AllowedValues': ['db.t3.micro', 'db.t3.small', 'db.t3.medium', 'db.t3.large'],
                    'Description': 'RDS instance type'
                },
                'KeyName': {
                    'Type': 'AWS::EC2::KeyPair::KeyName',
                    'Description': 'SSH key pair name'
                }
            },
            'Resources': {
                'VPC': {
                    'Type': 'AWS::EC2::VPC',
                    'Properties': {
                        'CidrBlock': '10.0.0.0/16',
                        'EnableDnsSupport': 'true',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': {'Ref': 'EnvironmentName'}
                            }
                        ]
                    }
                },
                'PublicSubnet': {
                    'Type': 'AWS::EC2::Subnet',
                    'Properties': {
                        'VpcId': {'Ref': 'VPC'},
                        'CidrBlock': '10.0.1.0/24',
                        'AvailabilityZone': {'Fn::Select': ['AWS::Region'], ['Select'], ['us-east-1a', 'us-east-1b', 'us-east-1c']},
                        'MapPublicIpOnLaunch': 'true',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': {'Ref': 'EnvironmentName'}
                            }
                        ]
                    }
                },
                'PrivateSubnet': {
                    'Type': 'AWS::EC2::Subnet',
                    'Properties': {
                        'VpcId': {'Ref': 'VPC'},
                        'CidrBlock': '10.0.2.0/24',
                        'AvailabilityZone': {'Fn::Select': ['AWS::Region'], ['Select'], ['us-east-1a', 'us-east-1b', 'us-east-1c']},
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': {'Ref': 'EnvironmentName'}
                            }
                        ]
                    }
                },
                'InternetGateway': {
                    'Type': 'AWS::EC2::InternetGateway',
                    'Properties': {
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': {'Ref': 'EnvironmentName'}
                            }
                        ]
                    }
                },
                'RouteTable': {
                    'Type': 'AWS::EC2::RouteTable',
                    'Properties': {
                        'VpcId': {'Ref': 'VPC'},
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': {'Ref': 'EnvironmentName'}
                            }
                        ]
                    }
                },
                'PublicRoute': {
                    'Type': 'AWS::EC2::Route',
                    'DependsOn': ['VPC', 'InternetGateway', 'RouteTable'],
                    'Properties': {
                        'RouteTableId': {'Ref': 'RouteTable'},
                        'DestinationCidrBlock': '0.0.0.0/0',
                        'GatewayId': {'Ref': 'InternetGateway'}
                    }
                },
                'SubnetRouteTableAssociation': {
                    'Type': 'AWS::EC2::SubnetRouteTableAssociation',
                    'Properties': {
                        'SubnetId': {'Ref': 'PublicSubnet'},
                        'RouteTableId': {'Ref': 'RouteTable'}
                    }
                },
                'EC2Instance': {
                    'Type': 'AWS::EC2::Instance',
                    'Properties': {
                        'InstanceType': {'Ref': 'InstanceType'},
                        'SubnetId': {'Ref': 'PublicSubnet'},
                        'ImageId': {'Fn::FindInMap': ['AWSRegionMap', {'Fn::FindInMap': ['AWS::Region', 'AMI', {'Ref': 'EnvironmentName'}}, 'AMI']},
                        'KeyName': {'Ref': 'KeyName'},
                        'SecurityGroupIds': [{'Ref': 'InstanceSecurityGroup'}],
                        'IamInstanceProfile': {'Ref': 'InstanceProfile'},
                        'UserData': {
                            'Fn::Base64': {
                                'Fn::Join': ['', [
                                    '#!/bin/bash',
                                    'yum update -y',
                                    'yum install -y git',
                                    'yum install -y python3 python3-pip',
                                    'pip3 install frappe-bench',
                                    'cd /opt',
                                    'bench init erpnext',
                                    'bench get-app https://github.com/frappe/erpnext',
                                    'bench new-site erpnext --db-root-password {{DBRootPassword}}',
                                    'bench --site erpnext install-app erpnext',
                                    'bench --site erpnext migrate',
                                    'bench --site erpnext configure redis-cache',
                                    'bench --site erpnext configure nginx',
                                    'bench --site erpnext start'
                                ], '']
                            }
                        }
                    },
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': {'Ref': 'EnvironmentName'}
                        },
                        {
                            'Key': 'Type',
                            'Value': 'ERPNext'
                        }
                    ]
                },
                'RDSInstance': {
                    'Type': 'AWS::RDS::DBInstance',
                    'Properties': {
                        'DBInstanceIdentifier': {'Fn::Sub': ['AWS::StackName', '-rds']},
                        'DBInstanceClass': {'Ref': 'DBInstanceClass'},
                        'Engine': 'mariadb',
                        'EngineVersion': '10.6',
                        'MasterUsername': 'admin',
                        'MasterUserPassword': '{{DBRootPassword}}',
                        'AllocatedStorage': '100',
                        'StorageType': 'gp2',
                        'DBName': 'erpnext',
                        'VPCSecurityGroups': [{'Ref': 'DatabaseSecurityGroup'}],
                        'DBSubnetGroupName': {'Ref': 'DBSubnetGroup'},
                        'BackupRetentionPeriod': '7',
                        'PreferredBackupWindow': '03:00-04:00',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': {'Ref': 'EnvironmentName'}
                            }
                        ]
                    }
                },
                'DatabaseSecurityGroup': {
                    'Type': 'AWS::EC2::SecurityGroup',
                    'Properties': {
                        'GroupDescription': 'Security group for RDS database',
                        'VpcId': {'Ref': 'VPC'},
                        'SecurityGroupIngress': [
                            {
                                'IpProtocol': 'tcp',
                                'FromPort': '3306',
                                'ToPort': '3306',
                                'SourceSecurityGroupId': {'Ref': 'InstanceSecurityGroup'}
                            }
                        ],
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': {'Ref': 'EnvironmentName'}
                            }
                        ]
                    }
                },
                'InstanceSecurityGroup': {
                    'Type': 'AWS::EC2::SecurityGroup',
                    'Properties': {
                        'GroupDescription': 'Security group for ERPNext instance',
                        'VpcId': {'Ref': 'VPC'},
                        'SecurityGroupIngress': [
                            {
                                'IpProtocol': 'tcp',
                                'FromPort': '80',
                                'ToPort': '80',
                                'CidrIp': '0.0.0.0/0'
                            },
                            {
                                'IpProtocol': 'tcp',
                                'FromPort': '443',
                                'ToPort': '443',
                                'CidrIp': '0.0.0.0/0'
                            },
                            {
                                'IpProtocol': 'tcp',
                                'FromPort': '22',
                                'ToPort': '22',
                                'CidrIp': '0.0.0.0/0'
                            }
                        ],
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': {'Ref': 'EnvironmentName'}
                            }
                        ]
                    }
                },
                'InstanceProfile': {
                    'Type': 'AWS::IAM::InstanceProfile',
                    'Properties': {
                        'Roles': [{'Ref': 'InstanceRole'}],
                        'InstanceProfileName': {'Fn::Sub': ['AWS::StackName', '-instance-profile']}
                    }
                },
                'InstanceRole': {
                    'Type': 'AWS::IAM::Role',
                    'Properties': {
                        'AssumeRolePolicyDocument': {
                            'Version': '2012-10-17',
                            'Statement': [
                                {
                                    'Effect': 'Allow',
                                    'Principal': {
                                        'Service': ['ec2.amazonaws.com']
                                    },
                                    'Action': [
                                        'ec2:Describe*',
                                        'ec2:RunInstances'
                                    ],
                                    'Resource': '*'
                                }
                            ]
                        },
                        'Path': '/',
                        'RoleName': {'Fn::Sub': ['AWS::StackName', '-instance-role']}
                    }
                },
                'ElasticLoadBalancer': {
                    'Type': 'AWS::ElasticLoadBalancing::LoadBalancer',
                    'Properties': {
                        'Subnets': [{'Ref': 'PublicSubnet'}],
                        'SecurityGroups': [{'Ref': 'InstanceSecurityGroup'}],
                        'Instances': [{'Ref': 'EC2Instance'}],
                        'Listeners': [
                            {
                                'LoadBalancerPort': '80',
                                'InstancePort': '80',
                                'Protocol': 'HTTP'
                            },
                            {
                                'LoadBalancerPort': '443',
                                'InstancePort': '443',
                                'Protocol': 'HTTPS',
                                'SSLCertificateId': {'Ref': 'SSLCertificate'}
                            }
                        ],
                        'HealthCheck': {
                            'TargetPort': '80',
                            'Interval': '30',
                            'Timeout': '5',
                            'HealthyThreshold': '2',
                            'UnhealthyThreshold': '2',
                            'Path': '/api/method/ping'
                        },
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': {'Ref': 'EnvironmentName'}
                            }
                        ]
                    }
                },
                'SSLCertificate': {
                    'Type': 'AWS::CertificateManager::Certificate',
                    'Properties': {
                        'DomainName': 'erpnext.yourdomain.com',
                        'ValidationMethod': 'DNS',
                        'SubjectAlternativeNames': ['erpnext.yourdomain.com', 'www.erpnext.yourdomain.com']
                    }
                },
                'AutoScalingGroup': {
                    'Type': 'AWS::AutoScaling::AutoScalingGroup',
                    'Properties': {
                        'VPCZoneIdentifier': {'Fn::Select': ['AWS::Region'], ['Select'], ['us-east-1a', 'us-east-1b', 'us-east-1c']},
                        'LaunchConfigurationName': {'Ref': 'LaunchConfig'},
                        'MinSize': '1',
                        'MaxSize': '10',
                        'DesiredCapacity': '2',
                        'TargetGroupARNs': [{'Ref': 'TargetGroupARN'}],
                        'HealthCheckType': 'EC2',
                        'HealthCheckGracePeriod': '300',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': {'Ref': 'EnvironmentName'}
                            }
                        ]
                    }
                },
                'LaunchConfig': {
                    'Type': 'AWS::AutoScaling::LaunchConfiguration',
                    'Properties': {
                        'InstanceType': {'Ref': 'InstanceType'},
                        'ImageId': {'Fn::FindInMap': ['AWSRegionMap', {'Fn::FindInMap': ['AWS::Region', 'AMI', {'Ref': 'EnvironmentName'}}, 'AMI']},
                        'SecurityGroups': [{'Ref': 'InstanceSecurityGroup'}],
                        'InstanceProfileName': {'Ref': 'InstanceProfile'},
                        'KeyName': {'Ref': 'KeyName'},
                        'UserData': {
                            'Fn::Base64': {
                                'Fn::Join': ['', [
                                    '#!/bin/bash',
                                    'echo "Starting ERPNext instance setup..."'
                                ], '']
                            }
                        }
                    }
                },
                'TargetGroup': {
                    'Type': 'AWS::ElasticLoadBalancingV2::TargetGroup',
                    'Properties': {
                        'TargetType': 'instance',
                        'TargetGroupAttributes': [
                            {
                                'Key': 'deregistration_delay.timeout_seconds',
                                'Value': '300'
                            }
                        ],
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': {'Ref': 'EnvironmentName'}
                            }
                        ]
                    }
                }
            },
            'Outputs': {
                'InstanceDNS': {
                    'Description': 'Public DNS name of the EC2 instance',
                    'Value': {'Fn::GetAtt': ['EC2Instance', 'PublicDnsName']}
                },
                'LoadBalancerDNS': {
                    'Description': 'DNS name of the load balancer',
                    'Value': {'Fn::GetAtt': ['ElasticLoadBalancer', 'DNSName']}
                },
                'RDSEndpoint': {
                    'Description': 'RDS instance endpoint',
                    'Value': {'Fn::GetAtt': ['RDSInstance', 'Endpoint.Address']}
                }
            }
        }
        
        return template
    
    def setup_auto_scaling(self):
        """Setup auto-scaling configuration"""
        
        return {
            'scaling_policies': [
                {
                    'policy_name': 'scale_out_on_cpu',
                    'metric_type': 'CPUUtilization',
                    'threshold': 70,  # 70% CPU utilization
                    'adjustment_type': 'ChangeInCapacity',
                    'scaling_adjustment': 1,  # Add 1 instance
                    'cooldown': 300  # 5 minutes
                },
                {
                    'policy_name': 'scale_in_on_cpu',
                    'metric_type': 'CPUUtilization',
                    'threshold': 20,  # 20% CPU utilization
                    'adjustment_type': 'ChangeInCapacity',
                    'scaling_adjustment': -1,  # Remove 1 instance
                    'cooldown': 300  # 5 minutes
                }
            ],
            'scheduled_scaling': [
                {
                    'name': 'business_hours_scale_out',
                    'schedule': 'cron(0 8 * * 1-5)',  # Weekdays 8 AM
                    'min_capacity': 3,
                    'max_capacity': 10,
                    'desired_capacity': 5
                },
                {
                    'name': 'business_hours_scale_in',
                    'schedule': 'cron(0 20 * * 1-5)',  # Weekdays 8 PM
                    'min_capacity': 1,
                    'max_capacity': 5,
                    'desired_capacity': 2
                }
            ]
        }
    
    def setup_monitoring(self):
        """Setup comprehensive monitoring"""
        
        return {
            'cloudwatch': {
                'metrics': [
                    'CPUUtilization',
                    'NetworkIn',
                    'NetworkOut',
                    'DiskReadOps',
                    'DiskWriteOps',
                    'DatabaseConnections'
                ],
                'alarms': [
                    {
                        'name': 'HighCPUUtilization',
                        'metric': 'CPUUtilization',
                        'threshold': 80,
                        'comparison': 'GreaterThanThreshold',
                        'evaluation_periods': 2,
                        'treat_missing_data': 'breaching'
                    },
                    {
                        'name': 'HighMemoryUtilization',
                        'metric': 'MemoryUtilization',
                        'threshold': 85,
                        'comparison': 'GreaterThanThreshold',
                        'evaluation_periods': 2,
                        'treat_missing_data': 'breaching'
                    },
                    {
                        'name': 'DatabaseConnectionErrors',
                        'metric': 'DatabaseConnections',
                        'threshold': 5,
                        'comparison': 'GreaterThanThreshold',
                        'evaluation_periods': 1,
                        'treat_missing_data': 'breaching'
                    }
                ],
                'dashboards': [
                    {
                        'name': 'ERPNextSystemOverview',
                        'widgets': [
                            {
                                'type': 'metric',
                                'properties': {
                                    'metric': 'CPUUtilization',
                                    'stat': 'Average',
                                    'period': 300,
                                    'region': self.region
                                }
                            },
                            {
                                'type': 'metric',
                                'properties': {
                                    'metric': 'MemoryUtilization',
                                    'stat': 'Average',
                                    'period': 300,
                                    'region': self.region
                                }
                            }
                        ]
                    }
                ]
            },
            'xray': {
                'tracing': True,
                'sampling_rate': 0.1,  # 10% sampling
                'annotations': {
                    'metadata': {
                        'environment': 'production',
                        'service': 'erpnext',
                        'version': 'v15.0.0'
                    }
                }
            }
        }
```

### 44.3 Azure Deployment

**Deploying ERPNext on Microsoft Azure**

```python
# Azure deployment configuration
class AzureDeployment:
    """Comprehensive Azure deployment for ERPNext"""
    
    def __init__(self):
        self.location = 'East US'
        self.resource_group = 'erpnext-rg'
        self.storage_account = self._setup_storage_account()
        self.virtual_network = self._setup_virtual_network()
        self.compute_resources = self._setup_compute()
        self.database_resources = self._setup_database()
    
    def create_arm_template(self):
        """Create Azure Resource Manager template"""
        
        template = {
            '$schema': 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#',
            'contentVersion': '1.0.0',
            'parameters': {
                'environmentName': {
                    'type': 'string',
                    'defaultValue': 'production',
                    'metadata': {
                        'description': 'Environment name for resources'
                    }
                },
                'adminUsername': {
                    'type': 'string',
                    'defaultValue': 'erpnextadmin',
                    'metadata': {
                        'description': 'Administrator username for VM'
                    }
                },
                'adminPassword': {
                    'type': 'secureString',
                    'metadata': {
                        'description': 'Administrator password for VM'
                    }
                },
                'vmSize': {
                    'type': 'string',
                    'defaultValue': 'Standard_D2s_v3',
                    'allowedValues': [
                        'Standard_B1s', 'Standard_B2s', 'Standard_D2s_v3',
                        'Standard_D4s_v3', 'Standard_D8s_v3'
                    ],
                    'metadata': {
                        'description': 'VM size for ERPNext'
                    }
                }
            },
            'resources': [
                {
                    'type': 'Microsoft.Network/virtualNetworks',
                    'apiVersion': '2020-05-01',
                    'name': '[concat(parameters(\'environmentName\'), \'-vnet\')]',
                    'location': '[resourceGroup().location]',
                    'properties': {
                        'addressSpace': {
                            'addressPrefixes': [
                                {
                                    'name': 'default',
                                    'addressPrefix': '10.0.0.0/16'
                                }
                            ]
                        },
                        'subnets': [
                            {
                                'name': 'web-subnet',
                                'properties': {
                                    'addressPrefix': '10.0.1.0/24',
                                    'networkSecurityGroup': '[concat(parameters(\'environmentName\'), \'-web-nsg\')]'
                                }
                            },
                            {
                                'name': 'db-subnet',
                                'properties': {
                                    'addressPrefix': '10.0.2.0/24',
                                    'networkSecurityGroup': '[concat(parameters(\'environmentName\'), \'-db-nsg\')]'
                                }
                            }
                        ]
                    }
                    },
                    'tags': {
                        'environment': '[parameters(\'environmentName\')]'
                    }
                },
                {
                    'type': 'Microsoft.Network/networkSecurityGroups',
                    'apiVersion': '2020-05-01',
                    'name': '[concat(parameters(\'environmentName\'), \'-web-nsg\')]',
                    'location': '[resourceGroup().location]',
                    'properties': {
                        'securityRules': [
                            {
                                'name': 'allow-http',
                                'properties': {
                                    'priority': 1000,
                                    'direction': 'Inbound',
                                    'access': 'Allow',
                                    'protocol': 'Tcp',
                                    'sourcePortRange': '80',
                                    'destinationAddressPrefix': '*',
                                    'destinationPortRange': '80'
                                }
                            },
                            {
                                'name': 'allow-https',
                                'properties': {
                                    'priority': 1001,
                                    'direction': 'Inbound',
                                    'access': 'Allow',
                                    'protocol': 'Tcp',
                                    'sourcePortRange': '443',
                                    'destinationAddressPrefix': '*',
                                    'destinationPortRange': '443'
                                }
                            },
                            {
                                'name': 'allow-ssh',
                                'properties': {
                                    'priority': 1002,
                                    'direction': 'Inbound',
                                    'access': 'Allow',
                                    'protocol': 'Tcp',
                                    'sourcePortRange': '22',
                                    'destinationAddressPrefix': '*',
                                    'destinationPortRange': '22'
                                }
                            }
                        ]
                    }
                },
                {
                    'type': 'Microsoft.Compute/virtualMachines',
                    'apiVersion': '2021-03-01',
                    'name': '[concat(parameters(\'environmentName\'), \'-vm\')]',
                    'location': '[resourceGroup().location]',
                    'properties': {
                        'hardwareProfile': {
                            'vmSize': '[parameters(\'vmSize\')]'
                        },
                        'osProfile': {
                            'computerName': '[concat(parameters(\'environmentName\'), \'-vm\')]',
                            'adminUsername': '[parameters(\'adminUsername\')]',
                            'adminPassword': '[parameters(\'adminPassword\')]',
                            'customData': '[base64(concat(\'#!/bin/bash\\nyum update -y\\nyum install -y git\\nyum install -y python3 python3-pip\\npip3 install frappe-bench\\ncd /opt\\nbench init erpnext\\nbench get-app https://github.com/frappe/erpnext\\nbench new-site erpnext --db-root-password [parameters(\'adminPassword\')]\\nbench --site erpnext install-app erpnext\\nbench --site erpnext migrate\\nbench --site erpnext configure redis-cache\\nbench --site erpnext configure nginx\\nbench --site erpnext start\\n\'))]'
                        },
                        'storageProfile': {
                            'imageReference': {
                                'id': '[resourceId(\'Microsoft.Compute/images/erpnext-image\')]'
                            },
                            'osDisk': {
                                'caching': 'ReadWrite',
                                'managedDisk': {
                                    'storageAccountType': 'Premium_LRS',
                                    'createOption': 'FromImage'
                                }
                            }
                        },
                        'networkProfile': {
                            'networkInterfaces': [
                                {
                                    'id': 'nic1',
                                    'properties': {
                                        'subnet': {
                                            'id': '[resourceId(\'Microsoft.Network/virtualNetworks/erpnext-vnet\')/subnets/web-subnet\')]'
                                        },
                                        'networkSecurityGroup': {
                                            'id': '[resourceId(\'Microsoft.Network/networkSecurityGroups/erpnext-web-nsg\')]'
                                        },
                                        'publicIPAddressConfiguration': {
                                            'name': 'erpnext-pip',
                                            'sku': {
                                                'name': 'Standard',
                                                'tier': 'Regional'
                                            },
                                            'idleTimeoutInMinutes': 10
                                        }
                                    }
                                }
                            ]
                        ]
                    }
                },
                {
                    'type': 'Microsoft.Network/publicIPAddresses',
                    'apiVersion': '2020-05-01',
                    'name': '[concat(parameters(\'environmentName\'), \'-pip\')]',
                    'location': '[resourceGroup().location]',
                    'sku': {
                        'name': 'Standard',
                        'tier': 'Regional'
                    },
                    'properties': {
                        'publicIPAllocationMethod': 'Static',
                        'idleTimeoutInMinutes': 10,
                        'dnsSettings': {
                            'domainNameLabel': 'erpnextdomain',
                            'fqdn': '[concat(parameters(\'environmentName\'), \'.erpnext.yourdomain.com\')]'
                        }
                    }
                },
                {
                    'type': 'Microsoft.DBforMariaDB/servers',
                    'apiVersion': '2018-06-01',
                    'name': '[concat(parameters(\'environmentName\'), \'-db\')]',
                    'location': '[resourceGroup().location]',
                    'sku': {
                        'name': 'B_Gen5',
                        'tier': 'GeneralPurpose'
                    },
                    'properties': {
                        'version': '10.6',
                        'administratorLogin': '[parameters(\'adminUsername\')]',
                        'administratorLoginPassword': '[parameters(\'adminPassword\')]',
                        'storageProfile': {
                            'storageMB': 51200,
                            'backupRetentionDays': 7
                        },
                        'createMode': 'Default',
                        'vnetResourceGroup': '[resourceGroup().name]',
                        'virtualNetworkSubnetId': '[resourceId(\'Microsoft.Network/virtualNetworks/erpnext-vnet\')/subnets/db-subnet\')]',
                        'publicNetworkAccess': 'Disabled'
                    }
                },
                {
                    'type': 'Microsoft.Storage/storageAccounts',
                    'apiVersion': '2021-04-01',
                    'name': '[concat(parameters(\'environmentName\'), \'storage\')]',
                    'location': '[resourceGroup().location]',
                    'sku': {
                        'name': 'Standard_LRS',
                        'tier': 'Standard'
                    },
                    'kind': 'StorageV2',
                    'properties': {
                        'accessTier': 'Hot',
                        'minimumTlsVersion': 'TLS1_2',
                        'supportsHttpsTrafficOnly': True,
                        'allowBlobPublicAccess': False,
                        'networkAcls': {
                            'defaultAction': 'Deny'
                        }
                    }
                },
                {
                    'type': 'Microsoft.Storage/storageAccounts/blobServices/containers',
                    'apiVersion': '2021-04-01',
                    'name': 'backups',
                    'dependsOn': [
                        '[resourceId(\'Microsoft.Storage/storageAccounts/erpnextstorage\')]'
                    ],
                    'properties': {
                        'publicAccess': 'None'
                    }
                },
                {
                    'type': 'Microsoft.Insights/diagnosticSettings',
                    'apiVersion': '2018-01-01',
                    'name': '[concat(parameters(\'environmentName\'), \'-diagnostics\')]',
                    'location': '[resourceGroup().location]',
                    'properties': {
                        'storageAccountId': '[resourceId(\'Microsoft.Storage/storageAccounts/erpnextstorage\')]',
                        'workspaceId': '[resourceId(\'Microsoft.OperationalInsights/workspaces/erpnext-workspace\')]',
                        'eventHubAuthorizationRuleId': '[resourceId(\'Microsoft.Insights/eventHubs/erpnext-eventhub\')]'
                    }
                }
            ]
        }
        
        return template
    
    def setup_azure_devops(self):
        """Setup Azure DevOps pipeline"""
        
        return {
            'azure_pipelines': {
                'name': 'ERPNext CI/CD Pipeline',
                'trigger': {
                    'branches': {
                        'include': ['main', 'develop'],
                        'exclude': []
                    }
                },
                'variables': {
                    'environment': 'production',
                    'vmSize': 'Standard_D2s_v3'
                },
                'stages': [
                    {
                        'stage': 'Build',
                        'jobs': [
                            {
                                'job': 'Build',
                                'steps': [
                                    {
                                        'task': 'UsePythonVersion',
                                        'inputs': {
                                            'versionSpec': {
                                                'versionSpec': '3.9'
                                            }
                                        }
                                    },
                                    {
                                        'task': 'Bash@3',
                                        'inputs': {
                                            'targetType': 'inline',
                                            'script': |
                                                pip install -r requirements.txt
                                                python -m pytest tests/ --cov=erpnext --cov-report=xml
                                        }
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'stage': 'Deploy',
                        'condition': 'succeeded()',
                        'dependsOn': 'Build',
                        'jobs': [
                            {
                                'job': 'DeployToStaging',
                                'steps': [
                                    {
                                        'task': 'AzureResourceGroupDeployment@2',
                                        'inputs': {
                                            'resourceGroupName': 'erpnext-staging-rg',
                                            'location': 'East US',
                                            'csmFileLink': '$(Pipeline.Workspace)/erpnext-staging.json',
                                            'csmParametersFileLink': '$(Pipeline.Workspace)/erpnext-staging-parameters.json'
                                        }
                                    }
                                ]
                            },
                            {
                                'job': 'SmokeTest',
                                'dependsOn': 'DeployToStaging',
                                'steps': [
                                    {
                                        'task': 'Bash@3',
                                        'inputs': {
                                            'targetType': 'inline',
                                            'script': |
                                                curl -f https://erpnext-staging.azurewebsites.net/api/method/ping
                                                if [ $? -eq 0 ]; then
                                                    echo "Smoke test passed"
                                                else
                                                    echo "Smoke test failed"
                                                    exit 1
                                                fi
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
```

### 44.4 Google Cloud Platform Deployment

**Deploying ERPNext on GCP**

```python
# GCP deployment configuration
class GCPDeployment:
    """Comprehensive GCP deployment for ERPNext"""
    
    def __init__(self):
        self.project_id = 'erpnext-project'
        self.region = 'us-central1'
        self.zone = 'us-central1-a'
        self.compute_engine = self._setup_compute_engine()
        self.cloud_sql = self._setup_cloud_sql()
        self.storage = self._setup_cloud_storage()
    
    def create_deployment_manager_template(self):
        """Create Deployment Manager template"""
        
        template = {
            'imports': [
                {
                    'path': 'deploymentmanager.v2',
                    'content': 'https://www.googleapis.com/deploymentmanager/v2'
                }
            ],
            'name': 'erpnext-deployment',
            'description': 'ERPNext deployment configuration',
            'target': {
                'config': {
                    'imports': [
                        {
                            'path': 'container.v1',
                            'content': 'https://container.googleapis.com/v1'
                        }
                    ],
                    'resources': [
                        {
                            'name': 'erpnext-cluster',
                            'type': 'container.v1.Cluster',
                            'properties': {
                                'zone': self.zone,
                                'initialNodeCount': 3,
                                'nodeConfig': {
                                    'machineType': 'e2-medium',
                                    'diskSizeGb': 50,
                                    'oauthScopes': [
                                        'https://www.googleapis.com/auth/cloud-platform'
                                    ]
                                }
                            }
                        },
                        {
                            'name': 'erpnext-node-pool',
                            'type': 'container.v1.NodePool',
                            'properties': {
                                'zone': self.zone,
                                'initialNodeCount': 3,
                                'nodeConfig': {
                                    'machineType': 'e2-medium',
                                    'diskSizeGb': 50,
                                    'oauthScopes': [
                                        'https://www.googleapis.com/auth/cloud-platform'
                                    ],
                                    'labels': {
                                        'environment': 'production',
                                        'service': 'erpnext'
                                    },
                                    'taints': [
                                        {
                                            'key': 'node-pool',
                                            'value': 'true'
                                        }
                                    ]
                                },
                                'autoscaling': {
                                    'enabled': True,
                                    'minNodeCount': 1,
                                    'maxNodeCount': 10
                                }
                            }
                        },
                        {
                            'name': 'erpnext-sql',
                            'type': 'sqladmin.v1.Database',
                            'properties': {
                                'region': self.region,
                                'databaseVersion': 'MYSQL_8_0',
                                'backendType': 'SECOND_GEN',
                                'instance': 'db-n1-standard-2',
                                'settings': {
                                    'tier': 'db-n1-standard-2',
                                    'ipConfiguration': {
                                        'ipv4Enabled': True,
                                        'privateNetwork': 'erpnext-vpc',
                                        'requireSsl': True
                                    },
                                    'backupConfiguration': {
                                        'enabled': True,
                                        'startTime': '03:00',
                                        'location': self.region
                                    },
                                    'databaseFlags': {
                                        'enable_4_byte': True
                                    }
                                }
                            }
                        },
                        {
                            'name': 'erpnext-bucket',
                            'type': 'storage.v1.Bucket',
                            'properties': {
                                'location': self.region,
                                'storageClass': 'STANDARD',
                                'uniformBucketLevelAccess': {
                                    'enabled': True
                                },
                                'lifecycle': {
                                    'rule': [
                                        {
                                            'action': {
                                                'type': 'SetStorageClass',
                                                'storageClass': 'NEARLINE'
                                            },
                                            'condition': {
                                                'age': 30,
                                                'matchesStorageClass': 'STANDARD'
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        }
        
        return template
    
    def setup_gke_workloads(self):
        """Setup GKE workloads for ERPNext"""
        
        return {
            'namespace': 'erpnext',
            'configmaps': {
                'erpnext-config': {
                    'data': {
                        'DB_HOST': '10.0.2.5',
                        'DB_PORT': '3306',
                        'REDIS_HOST': '10.0.2.6',
                        'REDIS_PORT': '6379',
                        'SITE_NAME': 'erpnext.yourdomain.com'
                    }
                }
            },
            'deployments': [
                {
                    'name': 'erpnext-web',
                    'labels': {
                        'app': 'erpnext-web',
                        'tier': 'frontend'
                    },
                    'spec': {
                        'replicas': 3,
                        'selector': {
                            'matchLabels': {
                                'app': 'erpnext-web'
                            }
                        },
                        'template': {
                            'metadata': {
                                'labels': {
                                    'app': 'erpnext-web'
                                }
                            },
                            'spec': {
                                'containers': [
                                    {
                                        'name': 'erpnext-web',
                                        'image': 'gcr.io/your-project/erpnext:latest',
                                        'ports': [
                                            {
                                                'containerPort': 80,
                                                'protocol': 'TCP'
                                            }
                                        ],
                                        'env': [
                                            {
                                                'name': 'DB_HOST',
                                                'valueFrom': {
                                                    'configMapKeyRef': 'erpnext-config',
                                                    'configMapKey': 'DB_HOST'
                                                }
                                            },
                                            {
                                                'name': 'DB_PORT',
                                                'valueFrom': {
                                                    'configMapKeyRef': 'erpnext-config',
                                                    'configMapKey': 'DB_PORT'
                                                }
                                            },
                                            {
                                                'name': 'SITE_NAME',
                                                'value': 'erpnext.yourdomain.com'
                                            }
                                        ],
                                        'resources': {
                                            'requests': {
                                                'memory': '512Mi',
                                                'cpu': '250m'
                                            },
                                            'limits': {
                                                'memory': '1Gi',
                                                'cpu': '500m'
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                },
                {
                    'name': 'erpnext-worker',
                    'labels': {
                        'app': 'erpnext-worker',
                        'tier': 'background'
                    },
                    'spec': {
                        'replicas': 2,
                        'selector': {
                            'matchLabels': {
                                'app': 'erpnext-worker'
                            }
                        },
                        'template': {
                            'metadata': {
                                'labels': {
                                    'app': 'erpnext-worker'
                                }
                            },
                            'spec': {
                                'containers': [
                                    {
                                        'name': 'erpnext-worker',
                                        'image': 'gcr.io/your-project/erpnext:latest',
                                        'env': [
                                            {
                                                'name': 'DB_HOST',
                                                'valueFrom': {
                                                    'configMapKeyRef': 'erpnext-config',
                                                    'configMapKey': 'DB_HOST'
                                                }
                                            },
                                            {
                                                'name': 'REDIS_HOST',
                                                'valueFrom': {
                                                    'configMapKeyRef': 'erpnext-config',
                                                    'configMapKey': 'REDIS_HOST'
                                                }
                                            }
                                        ],
                                        'resources': {
                                            'requests': {
                                                'memory': '1Gi',
                                                'cpu': '500m'
                                            },
                                            'limits': {
                                                'memory': '2Gi',
                                                'cpu': '1000m'
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            ]
        }
```

### 44.5 Container Orchestration with Kubernetes

**Kubernetes Deployment Patterns**

```python
# Kubernetes deployment patterns
class KubernetesDeployment:
    """Kubernetes deployment patterns for ERPNext"""
    
    def __init__(self):
        self.namespace = 'erpnext'
        self.deployment_strategy = 'RollingUpdate'
        self.service_types = ['ClusterIP', 'LoadBalancer', 'NodePort']
        self.ingress_config = self._setup_ingress()
    
    def create_kubernetes_manifests(self):
        """Create comprehensive Kubernetes manifests"""
        
        manifests = {
            'namespace': {
                'apiVersion': 'v1',
                'kind': 'Namespace',
                'metadata': {
                    'name': self.namespace,
                    'labels': {
                        'name': 'erpnext',
                        'environment': 'production'
                    }
                }
            },
            'configmap': {
                'apiVersion': 'v1',
                'kind': 'ConfigMap',
                'metadata': {
                    'name': 'erpnext-config',
                    'namespace': self.namespace
                },
                'data': {
                    'site_name': 'erpnext.yourdomain.com',
                    'db_host': 'erpnext-mysql',
                    'db_port': '3306',
                    'redis_host': 'erpnext-redis',
                    'redis_port': '6379',
                    'frappe_site_name': 'erpnext'
                }
            },
            'secret': {
                'apiVersion': 'v1',
                'kind': 'Secret',
                'metadata': {
                    'name': 'erpnext-secrets',
                    'namespace': self.namespace
                },
                'type': 'Opaque',
                'data': {
                    'db_password': '{{DB_PASSWORD}}',
                    'redis_password': '{{REDIS_PASSWORD}}',
                    'jwt_secret': '{{JWT_SECRET}}',
                    'encryption_key': '{{ENCRYPTION_KEY}}'
                }
            },
            'deployment': {
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {
                    'name': 'erpnext-web',
                    'namespace': self.namespace,
                    'labels': {
                        'app': 'erpnext',
                        'tier': 'frontend'
                    }
                },
                'spec': {
                    'replicas': 3,
                    'strategy': {
                        'type': 'RollingUpdate',
                        'rollingUpdate': {
                            'maxSurge': 1,
                            'maxUnavailable': 1
                        }
                    },
                    'selector': {
                        'matchLabels': {
                            'app': 'erpnext-web'
                        }
                    },
                    'template': {
                        'metadata': {
                            'labels': {
                                'app': 'erpnext',
                                'tier': 'frontend'
                            }
                        },
                        'spec': {
                            'containers': [
                                {
                                    'name': 'erpnext-web',
                                    'image': 'your-registry/erpnext:latest',
                                    'ports': [
                                        {
                                            'containerPort': 80,
                                            'protocol': 'TCP'
                                        }
                                    ],
                                    'env': [
                                        {
                                            'name': 'DB_HOST',
                                            'valueFrom': {
                                                'configMapKeyRef': 'erpnext-config',
                                                'configMapKey': 'db_host'
                                            }
                                        },
                                        {
                                            'name': 'DB_PORT',
                                            'valueFrom': {
                                                'configMapKeyRef': 'erpnext-config',
                                                'configMapKey': 'db_port'
                                            }
                                        },
                                        {
                                            'name': 'SITE_NAME',
                                            'valueFrom': {
                                                'configMapKeyRef': 'erpnext-config',
                                                'configMapKey': 'site_name'
                                            }
                                        }
                                    ],
                                    'resources': {
                                        'requests': {
                                            'memory': '512Mi',
                                            'cpu': '250m'
                                        },
                                        'limits': {
                                            'memory': '1Gi',
                                            'cpu': '500m'
                                        }
                                    },
                                    'livenessProbe': {
                                        'httpGet': {
                                            'path': '/api/method/ping',
                                            'port': 80
                                        },
                                        'initialDelaySeconds': 30,
                                        'periodSeconds': 10,
                                        'timeoutSeconds': 5,
                                        'failureThreshold': 3
                                    },
                                    'readinessProbe': {
                                        'httpGet': {
                                            'path': '/api/method/ready',
                                            'port': 80
                                        },
                                        'initialDelaySeconds': 5,
                                        'periodSeconds': 5,
                                        'timeoutSeconds': 3,
                                        'successThreshold': 1
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            'service': {
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {
                    'name': 'erpnext-web-service',
                    'namespace': self.namespace,
                    'labels': {
                        'app': 'erpnext',
                        'tier': 'frontend'
                    }
                },
                'spec': {
                    'selector': {
                        'app': 'erpnext'
                    },
                    'ports': [
                        {
                            'protocol': 'TCP',
                            'port': 80,
                            'targetPort': 80
                        }
                    ],
                    'type': 'ClusterIP'
                }
            },
            'ingress': {
                'apiVersion': 'networking.k8s.io/v1',
                'kind': 'Ingress',
                'metadata': {
                    'name': 'erpnext-ingress',
                    'namespace': self.namespace,
                    'annotations': {
                        'kubernetes.io/ingress.class': 'nginx',
                        'cert-manager.io/cluster-issuer': 'letsencrypt-prod',
                        'nginx.ingress.kubernetes.io/rewrite-target': '/api'
                    }
                },
                'spec': {
                    'tls': [
                        {
                            'hosts': ['erpnext.yourdomain.com', 'www.erpnext.yourdomain.com'],
                            'secretName': 'erpnext-tls'
                        }
                    ],
                    'rules': [
                        {
                            'host': 'erpnext.yourdomain.com',
                            'http': {
                                'paths': [
                                    {
                                        'path': '/api',
                                        'backend': {
                                            'serviceName': 'erpnext-web-service',
                                            'servicePort': 80
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            },
            'horizontalpodautoscaler': {
                'apiVersion': 'autoscaling/v2',
                'kind': 'HorizontalPodAutoscaler',
                'metadata': {
                    'name': 'erpnext-web-hpa',
                    'namespace': self.namespace
                },
                'spec': {
                    'scaleTargetRef': {
                        'apiVersion': 'apps/v1',
                        'kind': 'Deployment',
                        'name': 'erpnext-web'
                    },
                    'minReplicas': 1,
                    'maxReplicas': 10,
                    'metrics': [
                        {
                            'type': 'Resource',
                            'resource': {
                                'name': 'cpu',
                                'target': {
                                    'type': 'Utilization',
                                    'averageUtilization': 70
                                }
                            }
                        },
                        {
                            'type': 'Resource',
                            'resource': {
                                'name': 'memory',
                                'target': {
                                    'type': 'Utilization',
                                    'averageUtilization': 80
                                }
                            }
                        }
                    ]
                }
            }
        }
        
        return manifests
    
    def setup_monitoring(self):
        """Setup Kubernetes monitoring"""
        
        return {
            'prometheus': {
                'deployment': {
                    'name': 'prometheus',
                    'namespace': 'monitoring'
                },
                'service': {
                    'name': 'prometheus',
                    'namespace': 'monitoring'
                },
                'config': {
                    'global': {
                        'scrape_interval': '15s',
                        'evaluation_interval': '15s'
                    },
                    'scrape_configs': [
                        {
                            'job_name': 'kubernetes-apiservers',
                            'kubernetes_sd_configs': [
                                {
                                    'role': 'endpoints'
                                }
                            ],
                            'relabel_configs': [
                                {
                                    'source_labels': '__meta_kubernetes_namespace',
                                    'regex': '(.+)'
                                },
                                {
                                    'target_label': 'namespace',
                                    'regex': '(.+)'
                                }
                            ]
                        },
                        {
                            'job_name': 'kubernetes-pods',
                            'kubernetes_sd_configs': [
                                {
                                    'role': 'pod'
                                }
                            ],
                            'relabel_configs': [
                                {
                                    'source_labels': '__meta_kubernetes_pod_label_app',
                                    'regex': '(.+)'
                                },
                                {
                                    'target_label': 'app',
                                    'regex': '(.+)'
                                }
                            ]
                        }
                    ]
                }
            },
            'grafana': {
                'deployment': {
                    'name': 'grafana',
                    'namespace': 'monitoring'
                },
                'service': {
                    'name': 'grafana',
                    'namespace': 'monitoring'
                },
                'config': {
                    'GF_SECURITY_ADMIN_PASSWORD': 'admin123',
                    'GF_USERS_ALLOW_SIGN_UP': 'false',
                    'GF_INSTALL_PLUGINS': 'grafana-piechart-panel',
                    'GF_SERVER_DOMAIN': 'grafana.erpnext.yourdomain.com',
                    'GF_SERVER_ROOT_URL': 'https://grafana.erpnext.yourdomain.com'
                }
            }
        }
```

### 44.6 Cloud Security and Cost Management

**Security and Cost Optimization**

```python
# Cloud security and cost management
class CloudSecurityAndCosts:
    """Security and cost management for cloud deployments"""
    
    def __init__(self):
        self.security_policies = self._define_security_policies()
        self.cost_optimization = self._setup_cost_optimization()
        self.compliance_monitoring = self._setup_compliance_monitoring()
    
    def _define_security_policies(self):
        """Define comprehensive security policies"""
        
        return {
            'network_security': {
                'vpc_isolation': 'Separate VPC for each environment',
                'security_groups': 'Principle of least privilege',
                'nacls': 'Default deny, explicit allow',
                'vpn_access': 'VPN for administrative access',
                'ddos_protection': 'Cloudflare or AWS Shield'
            },
            'identity_and_access': {
                'iam_roles': 'Role-based access control',
                'mfa_required': 'Multi-factor authentication for all users',
                'password_policy': 'Strong passwords with rotation',
                'access_keys': 'Regular key rotation',
                'session_management': 'Secure session handling'
            },
            'data_protection': {
                'encryption_at_rest': 'Server-side encryption',
                'encryption_in_transit': 'TLS 1.3 everywhere',
                'key_management': 'Cloud KMS for key management',
                'backup_encryption': 'Encrypted backups',
                'data_classification': 'Classify and protect sensitive data'
            },
            'compliance': {
                'audit_logging': 'Comprehensive audit trails',
                'vulnerability_scanning': 'Regular security scanning',
                'penetration_testing': 'Periodic penetration testing',
                'compliance_certifications': 'SOC 2, ISO 27001, GDPR'
            }
        }
    
    def _setup_cost_optimization(self):
        """Setup cost optimization strategies"""
        
        return {
            'resource_optimization': {
                'right_sizing': 'Use appropriate instance sizes',
                'auto_scaling': 'Scale based on demand',
                'spot_instances': 'Use spot instances for non-critical workloads',
                'reserved_instances': 'Reserved instances for steady workloads',
                'scheduling': 'Schedule non-critical workloads for cost savings'
            },
            'storage_optimization': {
                'storage_classes': 'Use appropriate storage classes',
                'lifecycle_policies': 'Automate data lifecycle management',
                'compression': 'Enable compression for storage',
                'cdn_usage': 'Use CDN for static assets'
            },
            'network_optimization': {
                'data_transfer': 'Optimize data transfer patterns',
                'regional_deployment': 'Deploy in appropriate regions',
                'vpc_peering': 'Use VPC peering where possible',
                'load_balancing': 'Efficient load balancing'
            },
            'monitoring': {
                'cost_alerts': 'Set up cost alerts',
                'budget_tracking': 'Track spending against budgets',
                'resource_utilization': 'Monitor and optimize resource utilization',
                'anomaly_detection': 'Detect unusual spending patterns'
            }
        }
    
    def calculate_cost_projections(self, current_usage, growth_rate=0.2):
        """Calculate cost projections"""
        
        projections = {
            'monthly_costs': {},
            'annual_costs': {},
            'growth_projections': {}
        }
        
        for resource, current_cost in current_usage.items():
            # Calculate next 12 months with growth
            monthly_costs = []
            for month in range(1, 13):
                month_cost = current_cost * ((1 + growth_rate) ** month)
                monthly_costs.append(month_cost)
            
            projections['monthly_costs'][resource] = monthly_costs
            projections['annual_costs'][resource] = sum(monthly_costs)
        
        # Calculate growth projections
        projections['growth_projections'] = {
            '6_months': current_usage * ((1 + growth_rate) ** 6),
            '12_months': current_usage * ((1 + growth_rate) ** 12),
            '24_months': current_usage * ((1 + growth_rate) ** 24)
        }
        
        return projections
    
    def create_cost_dashboard_config(self):
        """Create cost dashboard configuration"""
        
        return {
            'dashboard_name': 'ERPNext Cost Dashboard',
            'widgets': [
                {
                    'type': 'cost_overview',
                    'title': 'Monthly Cost Overview',
                    'metrics': [
                        'Total Cost',
                        'Compute Cost',
                        'Storage Cost',
                        'Network Cost',
                        'Database Cost'
                    ],
                    'time_range': 'Last 30 days',
                    'visualization': 'pie_chart'
                },
                {
                    'type': 'cost_trends',
                    'title': 'Cost Trends',
                    'metrics': [
                        'Daily Cost',
                        'Weekly Cost',
                        'Monthly Cost'
                    ],
                    'time_range': 'Last 90 days',
                    'visualization': 'line_chart'
                },
                {
                    'type': 'resource_usage',
                    'title': 'Resource Utilization',
                    'metrics': [
                        'CPU Utilization',
                        'Memory Utilization',
                        'Disk Utilization',
                        'Network I/O'
                    ],
                    'time_range': 'Last 30 days',
                    'visualization': 'gauge_chart'
                },
                {
                    'type': 'cost_breakdown',
                    'title': 'Cost by Service',
                    'metrics': [
                        'Web Servers',
                        'Database',
                        'Storage',
                        'CDN',
                        'Load Balancer'
                    ],
                    'time_range': 'Last 30 days',
                    'visualization': 'bar_chart'
                }
            ],
            'alerts': [
                {
                    'name': 'High Cost Alert',
                    'condition': 'Total Cost > 1000',
                    'severity': 'Warning'
                },
                {
                    'name': 'Budget Exceeded Alert',
                    'condition': 'Total Cost > Budget',
                    'severity': 'Critical'
                },
                {
                    'name': 'Unusual Spending Alert',
                    'condition': 'Daily Cost > 2x Average',
                    'severity': 'Warning'
                }
            ]
        }
```

## 🎯 Chapter Summary

### Key Takeaways

1. **Choose the Right Cloud Platform**
   - Evaluate based on requirements (size, stack, cost sensitivity)
   - Consider ecosystem maturity and support options
   - Plan for multi-region deployment if needed
   - Factor in compliance and data residency requirements

2. **Implement Infrastructure as Code**
   - Use CloudFormation, ARM templates, or Deployment Manager
   - Version control all infrastructure configurations
   - Automate deployments with CI/CD pipelines
   - Implement proper testing and validation

3. **Optimize for Performance and Cost**
   - Use auto-scaling for variable workloads
   - Choose appropriate instance types and storage classes
   - Implement monitoring and alerting
   - Regular cost optimization and right-sizing

4. **Security and Compliance Are Critical**
   - Implement network security and isolation
   - Use identity and access management best practices
   - Encrypt data at rest and in transit
   - Regular security assessments and compliance checks

### Implementation Checklist

- [ ] **Platform Selection**: Choose appropriate cloud platform
- [ ] **Infrastructure Setup**: Deploy using IaC templates
- [ ] **Networking**: Configure VPC, subnets, and security groups
- [ ] **Compute**: Set up compute instances with auto-scaling
- [ ] **Database**: Deploy managed database with proper configuration
- [ ] **Storage**: Configure storage with lifecycle policies
- [ ] **Monitoring**: Set up comprehensive monitoring and alerting
- [ ] **Security**: Implement security best practices and compliance
- [ ] **Cost Optimization**: Set up cost monitoring and optimization
- [ ] **CI/CD**: Implement automated deployment pipelines

**Remember**: Cloud deployment provides scalability and reliability but requires proper planning, monitoring, and cost management to be effective.

---

**Next Chapter**: Advanced Topics and Future Trends
