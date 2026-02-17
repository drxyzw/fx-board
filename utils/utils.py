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