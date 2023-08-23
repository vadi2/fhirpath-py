from decimal import Decimal
import re
import fhirpathpy.engine.util as util
import fhirpathpy.engine.nodes as nodes

# This file holds code to hande the FHIRPath Existence functions (5.1 in the
# specification).

intRegex = re.compile(r"^[+-]?\d+$")
numRegex = re.compile(r"^[+-]?\d+(\.\d+)?$")


def iif_macro(ctx, data, cond, ok, fail=None):
    if util.is_true(cond(data)):
        return ok(data)
    elif fail:
        return fail(data)
    else:
        return []


def trace_fn(ctx, x, label=""):
    print("TRACE:[" + label + "]", str(x))
    return x


def to_integer(ctx, coll):
    if len(coll) != 1:
        return []

    value = util.get_data(coll[0])

    if value == False:
        return 0

    if value == True:
        return 1

    if util.is_number(value):
        if int(value) == value:
            return value

        return []

    if str(value):
        if re.match(intRegex, value) is not None:
            return int(value)

        raise Exception("Could not convert to ineger: " + value)

    return []


quantity_regex = re.compile(r"^((\+|-)?\d+(\.\d+)?)\s*(('[^']+')|([a-zA-Z]+))?$")
quantity_regex_map = {"value": 1, "unit": 5, "time": 6}


def to_quantity(ctx, coll, to_unit=None):
    result = None

    # Surround UCUM unit code in the to_unit parameter with single quotes
    if to_unit and not nodes.FP_Quantity.timeUnitsToUCUM.get(to_unit):
        to_unit = f"'{to_unit}'"

    if len(coll) > 1:
        raise Exception("Could not convert to quantity: input collection contains multiple items")
    elif len(coll) == 1:
        v = util.get_data(coll[0])
        quantity_regex_res = None

        if isinstance(v, (int, Decimal)):
            result = nodes.FP_Quantity(v, "'1'")
        elif isinstance(v, nodes.FP_Quantity):
            result = v
        elif isinstance(v, bool):
            result = nodes.FP_Quantity(1 if v else 0, "'1'")
        elif isinstance(v, str):
            quantity_regex_res = quantity_regex.match(v)

        if quantity_regex_res:
            value = quantity_regex_res.group(quantity_regex_map["value"])
            unit = quantity_regex_res.group(quantity_regex_map["unit"])
            time = quantity_regex_res.group(quantity_regex_map["time"])

            # UCUM unit code in the input string must be surrounded with single quotes
            if not time or nodes.FP_Quantity.timeUnitsToUCUM.get(time):
                result = nodes.FP_Quantity(Decimal(value), unit or time or "'1'")

        if result and to_unit and result.unit != to_unit:
            result = nodes.FP_Quantity.conv_unit_to(result.unit, result.value, to_unit)

    return result if result else []


def to_decimal(ctx, coll):
    if len(coll) != 1:
        return []

    value = util.get_data(coll[0])

    if value is False:
        return 0

    if value is True:
        return 1.0

    if util.is_number(value):
        return value

    if isinstance(value, str):
        if re.match(numRegex, value) is not None:
            return Decimal(value)

        raise Exception("Could not convert to decimal: " + value)

    return []


def to_string(ctx, coll):
    if len(coll) != 1:
        return []

    value = util.get_data(coll[0])
    return str(value)


# Defines a function on engine called to+timeType (e.g., toDateTime, etc.).
# @param timeType The string name of a class for a time type (e.g. "FP_DateTime").


def to_date_time(ctx, coll):
    ln = len(coll)
    rtn = []
    if ln > 1:
        raise Exception("to_date_time called for a collection of length " + ln)

    if ln == 1:
        value = util.get_data(coll[0])

        dateTimeObject = nodes.FP_DateTime(value)

        if dateTimeObject:
            rtn.append(dateTimeObject)

    return rtn


def to_time(ctx, coll):
    ln = len(coll)
    rtn = []
    if ln > 1:
        raise Exception("to_time called for a collection of length " + ln)

    if ln == 1:
        value = util.get_data(coll[0])

        timeObject = nodes.FP_Time(value)

        if timeObject:
            rtn.append(timeObject)

    return rtn


def to_date(ctx, coll):
    ln = len(coll)
    rtn = []

    if ln > 1:
        raise Exception("to_date called for a collection of length " + ln)

    if ln == 1:
        value = util.get_data(coll[0])

        dateObject = nodes.FP_DateTime(value)

        if dateObject:
            rtn.append(dateObject)

    return rtn
