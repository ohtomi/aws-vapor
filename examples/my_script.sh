#!/bin/bash -xe
yum update -y
yum update -y aws-cfn-bootstrap
/opt/aws/bin/cfn-init -v --stack {{ stack_id }} --resource {{ resource_name }} --region {{ region }}
/opt/aws/bin/cfn-signal -e $? --stack {{ stack_id }} --resource {{ resource_name }} --region {{ region }}
