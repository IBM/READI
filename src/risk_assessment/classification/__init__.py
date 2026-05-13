from typing import cast

from risk_assessment.classification.identifiers import Identifier


def create_instance(identifier_fqn: str) -> Identifier:
    parts = identifier_fqn.split(".")
    module_name = ".".join(parts[:-1])
    module = __import__(module_name)
    for comp in parts[1:]:
        module = getattr(module, comp)

    if type(module) is type(Identifier):
        m = module()
        return cast(Identifier, m)

    raise ValueError(
        f"{identifier_fqn} does not exists or is not a subclass of `risk_assessment.classification.identifiers.Identifier`"
    )


def create_instance_if_required(identifier: Identifier | str) -> Identifier:
    if isinstance(identifier, Identifier):
        return identifier
    else:
        return create_instance(identifier)


def build_identifiers(specs: list[Identifier | str]) -> list[Identifier]:
    return [create_instance_if_required(identifier) for identifier in specs]
