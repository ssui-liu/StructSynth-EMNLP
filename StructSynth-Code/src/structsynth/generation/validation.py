"""Training-derived field schemas, response validation and table assembly."""

from __future__ import annotations

import math

import pandas as pd

from .errors import GenerationError
from .serialization import same_scalar, scalar


def infer_schema(train, records, *, spec, columns):
    categorical = set(spec.categorical_columns)
    integer = set(getattr(spec, "integer_columns", []))
    boolean = set(getattr(spec, "boolean_columns", []))
    nullable = set(getattr(spec, "nullable_columns", []))
    configured_categories = getattr(spec, "categories", {})
    categorical.update(configured_categories)
    target = spec.target_column
    if spec.task_type == "classification":
        categorical.add(target)
    if not (categorical | integer | boolean | nullable).issubset(columns):
        raise ValueError("Column type declarations contain unknown columns")
    if not set(configured_categories).issubset(columns):
        raise ValueError("Configured categories contain unknown columns")
    result = {}
    for column in columns:
        values = [row[column] for row in records if row[column] is not None]
        if column in boolean or pd.api.types.is_bool_dtype(train[column].dtype):
            kind = "boolean"
        elif column in integer or pd.api.types.is_integer_dtype(train[column].dtype):
            kind = "integer"
        elif column in categorical:
            domain = values or [scalar(value) for value in configured_categories.get(column, [])]
            kinds = {type(value) for value in domain if value is not None}
            if kinds == {str}:
                kind = "string"
            elif kinds == {bool}:
                kind = "boolean"
            elif kinds == {int}:
                kind = "integer"
            elif kinds and kinds.issubset({int, float}):
                kind = "number"
            else:
                raise ValueError("Categorical column %r needs nonempty, consistently typed training values" % column)
        else:
            if not pd.api.types.is_numeric_dtype(train[column].dtype):
                raise ValueError("Non-numeric column %r must be declared categorical" % column)
            kind = "number"
        schema = {"type": kind, "nullable": column in nullable}
        if column in categorical:
            categories = configured_categories.get(column, values)
            unique = []
            for value in categories:
                value = scalar(value)
                if value is not None and not any(same_scalar(value, item) for item in unique):
                    unique.append(value)
            if not unique:
                raise ValueError("Categorical column %r has no allowed values" % column)
            # Limited training examples do not establish the full support
            # of non-target categorical features. Only explicit domains and
            # classification labels are closed sets.
            constrained = column in configured_categories or (
                column == target and spec.task_type == "classification")
            schema["enum" if constrained else "observed_values"] = unique
        result[column] = schema
    return result


def value_error(field_schema, column, value):
    schema = field_schema[column]
    if value is None:
        return None if schema["nullable"] else "%s does not allow null" % column
    kind = schema["type"]
    valid = ((kind == "integer" and type(value) is int) or
             (kind == "number" and type(value) in (int, float)) or
             (kind == "boolean" and type(value) is bool) or
             (kind == "string" and type(value) is str))
    if not valid:
        return "%s must have JSON type %s" % (column, kind)
    if kind == "integer" and not -(2 ** 63) <= value < 2 ** 63:
        return "%s must fit a signed 64-bit integer" % column
    if kind == "number":
        try:
            finite = math.isfinite(float(value))
        except OverflowError:
            finite = False
        if not finite:
            return "%s must be a finite 64-bit floating-point value" % column
    if "enum" in schema and not any(
            same_scalar(value, item) or
            (kind in ("integer", "number") and type(item) in (int, float) and value == item)
            for item in schema["enum"]):
        return "%s is outside the allowed categories" % column
    return None


def validate_response(content, requested_ids, variables, *, field_schema):
    if not isinstance(content, dict) or set(content) != {"rows"} or not isinstance(content["rows"], list):
        return {}, ["Response must contain exactly a rows list"]
    requested = set(requested_ids)
    seen = set()
    # An invalid envelope/unknown ID/duplicate ID makes the entire response
    # ambiguous. Never quietly take its first record or truncate extra rows.
    for row in content["rows"]:
        if not isinstance(row, dict) or set(row) != {"row_id", "values"}:
            return {}, ["Every row must contain exactly row_id and values"]
        row_id = row["row_id"]
        if type(row_id) is not int or row_id not in requested:
            return {}, ["Response contains an unknown or non-integer row_id"]
        if row_id in seen:
            return {}, ["Response contains duplicate row_id %s" % row_id]
        seen.add(row_id)
    accepted = {}
    errors = []
    for row in content["rows"]:
        row_id, values = row["row_id"], row["values"]
        if not isinstance(values, dict) or set(values) != set(variables):
            errors.append("row_id %s must contain exactly generated columns %s" % (row_id, variables))
            continue
        row_errors = [value_error(field_schema, column, values[column]) for column in variables]
        row_errors = [error for error in row_errors if error]
        if row_errors:
            errors.extend("row_id %s: %s" % (row_id, error) for error in row_errors)
        else:
            accepted[row_id] = dict(values)
    return accepted, errors


def assemble(rows, columns, field_schema):
    for row_id, values in rows.items():
        if set(values) != set(columns):
            raise GenerationError("Generated row %s is incomplete" % row_id, row_ids=[row_id])
    frame = pd.DataFrame([rows[row_id] for row_id in sorted(rows)], columns=columns)
    for column, schema in field_schema.items():
        if schema["type"] == "integer":
            frame[column] = frame[column].astype("Int64" if schema["nullable"] else "int64")
        elif schema["type"] == "boolean":
            frame[column] = frame[column].astype("boolean" if schema["nullable"] else "bool")
        elif schema["type"] == "number":
            frame[column] = frame[column].astype("float64")
    return frame
