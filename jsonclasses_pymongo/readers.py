from __future__ import annotations
from typing import Any, Optional
from datetime import date, datetime
from enum import Enum


def readstr(val: Any) -> Optional[str]:
    if val in ['null', 'NULL', 'nil', 'None', 'NONE']:
        return None
    if type(val) is str:
        return val
    return str(val)


def readint(val: Any) -> Optional[int]:
    if val in ['null', 'NULL', 'nil', 'None', 'NONE']:
        return None
    if type(val) is int:
        return val
    return int(val)


def readfloat(val: Any) -> Optional[float]:
    if val in ['null', 'NULL', 'nil', 'None', 'NONE']:
        return None
    if type(val) is float:
        return val
    return float(val)


def readbool(val: Any) -> Optional[bool]:
    if val in ['null', 'NULL', 'nil', 'None', 'NONE']:
        return None
    if type(val) is bool:
        return val
    if val in ['true', 'True', 'TRUE', 'YES']:
        return True
    elif val in ['false', 'False', 'FALSE', 'NO']:
        return False
    else:
        raise ValueError('value is not valid bool str')


def readdate(val: Any) -> Optional[datetime]:
    if val in ['null', 'NULL', 'nil', 'None', 'NONE']:
        return None
    if type(val) is date:
        return datetime(val.year, val.month, val.day)
    if type(val) is datetime:
        d = date(val.year, val.month, val.day)
        return datetime(d.year, d.month, d.day)
    if type(val) is str:
        d = date.fromisoformat(val[:10])
        return datetime(d.year, d.month, d.day)
    if type(val) is float or type(val) is int:
        dt = datetime.fromtimestamp(val)
        d = date(dt.year, dt.month, dt.day)
        return datetime(d.year, d.month, d.day)
    raise ValueError('value is not valid date value')


def readdatetime(val: Any) -> Optional[datetime]:
    if val in ['null', 'NULL', 'nil', 'None', 'NONE']:
        return None
    if type(val) is date:
        return datetime(val.year, val.month, val.day)
    if type(val) is datetime:
        return val
    if type(val) is str:
        return datetime.fromisoformat(val.replace('Z', ''))
    if type(val) is float or type(val) is int:
        return datetime.fromtimestamp(val)
    raise ValueError('value is not valid datetime value')


def readenum(val: Any, cls: type[Enum]) -> Optional[Any]:
    if val in ['null', 'nil', 'None']:
        return None
    if type(val) is int:
        return cls(val).value
    if type(val) is str:
        try:
            return cls(val).value
        except:
            try:
                return cls(int(val)).value
            except:
                try:
                    return cls[val].value
                except:
                    try:
                        return cls[val.upper()].value
                    except:
                        pass
    if type(val) is cls:
        return val.value
    raise ValueError(f'value is not valid enum {cls.__name__} value')


def readorder(val: Any) -> int:
    if type(val) is int:
        return val
    if type(val) is str:
        if val in ['ASC', 'asc', 'Asc']:
            return 1
        elif val in ['DESC', 'desc', 'Desc']:
            return -1
        else:
            return int(val)
    raise ValueError('value is not valid order descriptor')
