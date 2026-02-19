from dateutil.relativedelta import relativedelta as dt

def freqToString(freq):
    freq_label = ""
    if freq == "D":
        freq_label = "Daily"
    elif freq == "M":
        freq_label = "Monthly"
    elif freq == "A":
        freq_label = "Annually"
    else:
        raise ValueError("Invalid freq:" + freq)
    return freq_label

def parseTimeDelta(dtStr):
    unit = dtStr[-1].upper()
    length = int(dtStr[:-1])
    if unit == "Y":
        return dt(years=length)
    elif unit == "M":
        return dt(months=length)
    elif unit == "W":
        return dt(weeks=length)
    elif unit == "D":
        return dt(days=length)
    else:
        raise ValueError(f"Invalid date unit: {unit}")
    return

    
    