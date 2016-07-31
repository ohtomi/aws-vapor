# -*- coding: utf-8 -*-

from aws_vapor.dsl import (
    Template, Parameter, Mapping, Condition, Resource, Output,
    Attributes, Intrinsics, Pseudos,
    UserData, CfnInitMetadata
)


def recipe(t):
    t.parameters(Parameter('EnvType')
        .default('prod')
    , merge=True)
