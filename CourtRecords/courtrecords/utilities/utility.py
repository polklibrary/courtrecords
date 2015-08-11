from pyramid.httpexceptions import HTTPForbidden
import datetime

def has_interface(cls,interface):
    if not hasattr(cls,interface):
        raise HTTPForbidden()

def FindInList(l,name,target,default={}):
    nl = filter(lambda x: x[name] == target, l)
    if nl:
        return nl.pop()
    else:
        return default

def Results2Dict(rows,purge=[]):
    results = []
    for row in rows:
        d = {}
        for column in row.__table__.columns:
            if column.name not in purge:
                if isinstance(getattr(row, column.name), datetime.datetime):
                    d[column.name] = getattr(row, column.name).strftime('%m/%d/%Y %I:%M %p')
                elif isinstance(getattr(row, column.name), unicode):
                    d[column.name] = str(getattr(row, column.name))
                elif isinstance(getattr(row, column.name), long):
                    d[column.name] = int(getattr(row, column.name))
                else:
                    d[column.name] = getattr(row, column.name)

        results.append(d)
    return results

def Result2Dict(row,purge=[],replace={}):
    d = {}
    for column in row.__table__.columns:
        if column.name not in purge:
            if isinstance(getattr(row, column.name), datetime.datetime):
                d[column.name] = getattr(row, column.name).strftime('%m/%d/%Y %I:%M %p')
            else:
                d[column.name] = getattr(row, column.name)
        if column.name in replace:
            for k,v in replace.items():
                d[k] = v
    return d
