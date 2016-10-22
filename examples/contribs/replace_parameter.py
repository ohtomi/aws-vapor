# -*- coding: utf-8 -*-

from aws_vapor.dsl import Template
from aws_vapor.dsl import Metadata
from aws_vapor.dsl import Parameter
from aws_vapor.dsl import Mapping
from aws_vapor.dsl import Condition
from aws_vapor.dsl import Resource
from aws_vapor.dsl import Output
from aws_vapor.dsl import Attributes
from aws_vapor.dsl import Intrinsics
from aws_vapor.dsl import Pseudos
from aws_vapor.dsl import UserData
from aws_vapor.dsl import CfnInitMetadata


def recipe(t):
    t.parameters(Parameter('EnvType')
        .default('prod')
    , merge=True)
