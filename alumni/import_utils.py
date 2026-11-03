import re
from datetime import date, datetime
from openpyxl import load_workbook

ALLOWED_BRANCHES = {"kharghar", "panvel", "koperkhairane"}
REQUIRED_FIELDS = {"name", "mobile"}
OPTIONAL_FIELDS = {"previous_course", "admission_year", "email"}
ALLOWED_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS


def normalize_mobile(value):
    if value is None or isinstance(value, bool):
        return ""

    if isinstance(value, (int, float)):
        if isinstance(value, float) and not value.is_integer():
            return ""
        value = str(int(value))

    value = str(value).strip()
    digits = re.sub(r"\D", "", value)

    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]

    if len(digits) != 10 or digits[0] not in "6789":
        return ""

    return digits


def parse_year(value):
    if value is None or str(value).strip() == "":
        return None

    if isinstance(value, (date, datetime)):
        year = value.year
    else:
        text = str(value).strip()
        if re.fullmatch(r"\d{4}(?:\.0)?", text):
            year = int(float(text))
        else:
            raise ValueError("Invalid admission year")

    if not 2013 <= year <= 2025:
        raise ValueError("Year outside 2013–2025")

    return year


def inspect_workbook(upload):
    upload.seek(0)
    workbook = load_workbook(upload, read_only=True, data_only=True)
    try:
        result = []
        for sheet in workbook.worksheets:
            first = next(
                sheet.iter_rows(min_row=1, max_row=1, values_only=True),
                ()
            )
            result.append({
                "sheet": sheet.title,
                "headers": [
                    str(value).strip() if value is not None else ""
                    for value in first
                ],
                "rows": sheet.max_row,
            })
        return result
    finally:
        workbook.close()


def validate_mapping(mapping):
    if not isinstance(mapping, dict):
        raise ValueError("Column mapping must be an object")

    if not REQUIRED_FIELDS.issubset(mapping):
        raise ValueError("Name and mobile mappings are required")

    if set(mapping) - ALLOWED_FIELDS:
        raise ValueError("Unapproved target field")

    positions = list(mapping.values())

    if any(type(pos) is not int or pos < 0 for pos in positions):
        raise ValueError("Invalid column position")

    if len(set(positions)) != len(positions):
        raise ValueError("A column cannot map to multiple fields")

    return True


def preview_rows(upload, sheet_name, mapping, limit=20):
    validate_mapping(mapping)
    upload.seek(0)
    workbook = load_workbook(upload, read_only=True, data_only=True)

    try:
        if sheet_name not in workbook.sheetnames:
            raise ValueError("Sheet not found")

        sheet = workbook[sheet_name]
        preview = []

        for excel_row, row in enumerate(
            sheet.iter_rows(min_row=2, values_only=True),
            start=2
        ):
            if not any(value is not None and str(value).strip() for value in row):
                continue

            record = {}
            for field, index in mapping.items():
                value = row[index] if index < len(row) else None
                record[field] = value

            name = str(record.get("name") or "").strip()
            mobile = normalize_mobile(record.get("mobile"))

            errors = []
            if not name:
                errors.append("Missing name")
            if not mobile:
                errors.append("Invalid mobile")

            if "admission_year" in mapping:
                try:
                    record["admission_year"] = parse_year(
                        record.get("admission_year")
                    )
                except ValueError as exc:
                    errors.append(str(exc))

            preview.append({
                "excel_row": excel_row,
                "data": record,
                "errors": errors,
            })

            if len(preview) >= limit:
                break

        return preview
    finally:
        workbook.close()
