from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from beartype import beartype


@beartype
@dataclass(frozen=True)
class ValidationIssue:
    code: str
    level: str
    path: str
    message: str


@beartype
@dataclass(frozen=True)
class ValidationRule:
    code: str
    level: str
    message: str


@beartype
@dataclass(frozen=True)
class ValidationSpec:
    system_rules: dict[str, ValidationRule]
    primitive_rules: dict[str, dict[str, ValidationRule]]
    cross_object_rules: dict[str, ValidationRule]

    def rule(self, section: str, key: str, primitive: str | None = None) -> ValidationRule:
        if section == "system":
            return self.system_rules[key]
        if section == "cross_object":
            return self.cross_object_rules[key]
        if primitive is None:
            raise KeyError(f"Primitive rule {key!r} requires primitive name")
        return self.primitive_rules[primitive][key]


@beartype
class ValidationError(ValueError):
    def __init__(self, issues: list[ValidationIssue]):
        self.issues = issues
        super().__init__(issues[0].message if issues else "Validation failed")


@beartype
class ValidationRegistry:
    def __init__(self, spec: ValidationSpec):
        self.spec = spec

    def system_issue(self, key: str, *, path: str, **format_args: object) -> ValidationIssue:
        rule = self.spec.rule("system", key)
        return ValidationIssue(rule.code, rule.level, path, rule.message.format(**format_args))

    def primitive_issue(self, primitive: str, key: str, *, path: str, **format_args: object) -> ValidationIssue:
        rule = self.spec.rule("primitive", key, primitive=primitive)
        return ValidationIssue(rule.code, rule.level, path, rule.message.format(**format_args))

    def cross_object_issue(self, key: str, *, path: str, **format_args: object) -> ValidationIssue:
        rule = self.spec.rule("cross_object", key)
        return ValidationIssue(rule.code, rule.level, path, rule.message.format(**format_args))

    def raise_issue(self, issue: ValidationIssue) -> None:
        raise ValidationError([issue])


@lru_cache(maxsize=1)
def load_validation_spec() -> ValidationSpec:
    raw = _parse_simple_yaml(_validation_spec_path().read_text())
    return ValidationSpec(
        system_rules=_build_rules(raw["system_rules"]),
        primitive_rules={primitive: _build_rules(rules) for primitive, rules in raw["primitive_rules"].items()},
        cross_object_rules=_build_rules(raw["cross_object_rules"]),
    )


@lru_cache(maxsize=1)
def validation_registry() -> ValidationRegistry:
    return ValidationRegistry(load_validation_spec())


def _validation_spec_path() -> Path:
    return Path(__file__).resolve().parent / "rules" / "validation.yaml"


@beartype
def _build_rules(raw_rules: dict[str, dict[str, str]]) -> dict[str, ValidationRule]:
    return {
        key: ValidationRule(code=value["code"], level=value["level"], message=value["message"])
        for key, value in raw_rules.items()
    }


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, _, value = line.strip().partition(":")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        current = stack[-1][1]
        if value.strip() == "":
            node: dict[str, Any] = {}
            current[key] = node
            stack.append((indent, node))
            continue
        current[key] = value.strip().strip('"')
    return root
