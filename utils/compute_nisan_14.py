"""Recompute 14 Nisan for each Passover of Pilate's prefecture and write it into chronology.json.

    uvx --with ephem python utils/compute_nisan_14.py

Writes crucifixion_year.nisan_14 in docs/data/chronology.json, which the year-of-the-cross chart
and chronology/dating-the-cross.md read. Everything else in the file is left as it is.

The method is the one the first-century calendar used, approximated:

- the month begins on the evening the new crescent is first seen from Jerusalem. Visibility is a
  rough test of the moon's age at sunset and how long it stays up after the sun. Three thresholds
  are run, a usual one (20 hours, 45 minutes), an early one (15 hours, 30 minutes) and a late one (25
  hours, 60 minutes), because whether a thin crescent was seen, or missed in haze, is exactly what
  moves a Passover by a day. A year whose early or late sighting changes the weekday is marginal;
- Nisan is the first month whose 15th day falls on or after the spring equinox. The month after it
  is reported too, for a year a calendar court may have lengthened with a second Adar.

PyEphem gives Julian-calendar dates before 1582, which is the calendar the sources use. Weekdays are
taken from the Julian day number, so they do not depend on any calendar conversion.
"""

import json
import math
from pathlib import Path

import ephem

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "docs" / "data" / "chronology.json"
FIRST, LAST = 26, 36  # Pontius Pilate's prefecture
THRESHOLDS = {"usual": (20, 45), "early": (15, 30), "late": (25, 60)}  # moon age at sunset (h), moonset lag (min)
WEEKDAYS = "Sunday Monday Tuesday Wednesday Thursday Friday Saturday".split()
MONTHS = ",January,February,March,April,May,June".split(",")

JERUSALEM = ephem.Observer()
JERUSALEM.lat, JERUSALEM.lon, JERUSALEM.elevation = "31.778", "35.235", 750
JERUSALEM.pressure = 0
JERUSALEM.horizon = "-0:34"


def weekday(d):
    jd = float(d) + 2415020.0  # PyEphem counts from noon, 31 December 1899
    return WEEKDAYS[int(math.floor(jd + 0.5) + 1) % 7]


def civil(d):
    y, m, day = ephem.Date(d).triple()
    return {"date": f"{int(day)} {MONTHS[m]}", "weekday": weekday(d)}


def first_crescent(new_moon, age_h, lag_min):
    """The sunset on which the new crescent is first seen."""
    for k in range(5):
        JERUSALEM.date = ephem.Date(new_moon - 0.5 + k)
        sunset = JERUSALEM.next_setting(ephem.Sun())
        if sunset < new_moon:
            continue
        JERUSALEM.date = sunset
        lag = (JERUSALEM.next_setting(ephem.Moon()) - sunset) * 1440
        if (sunset - new_moon) * 24 >= age_h and lag >= lag_min:
            return sunset
    raise ValueError(f"no crescent within five days of {ephem.Date(new_moon)}")


def fourteenth(new_moon, threshold):
    # Nisan 1 begins at the sighting; the daylight of 14 Nisan is fourteen civil days on.
    return ephem.Date(first_crescent(new_moon, *THRESHOLDS[threshold]) + 14)


def month(new_moon):
    """14 Nisan on the usual sighting, and on an early or late one where that moves the date."""
    usual = civil(fourteenth(new_moon, "usual"))
    out = dict(usual)
    for name in ("early", "late"):
        alt = civil(fourteenth(new_moon, name))
        out[f"{name}_crescent"] = alt if alt["date"] != usual["date"] else None
    return out


def weekdays(m):
    return [m["weekday"]] + [m[k]["weekday"] for k in ("early_crescent", "late_crescent") if m[k]]


def passover(year):
    equinox = ephem.next_vernal_equinox(f"{year}/1/1")
    moon = ephem.next_new_moon(ephem.Date(equinox - 30))
    while fourteenth(moon, "usual") + 1 < equinox:  # 15 Nisan before the equinox: not yet Nisan
        moon = ephem.next_new_moon(ephem.Date(moon + 1))
    later = ephem.next_new_moon(ephem.Date(moon + 1))
    row = {"year": year, **month(moon)}
    row["second_adar"] = month(later)
    row["friday"] = "Friday" in weekdays(row)
    # How close the feast sits to the equinox: a Passover at the equinox itself is the kind a
    # calendar court was likeliest to push a month later.
    row["days_after_equinox"] = int(math.floor(fourteenth(moon, "usual") + 1 - equinox))
    return row


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    rows = [passover(y) for y in range(FIRST, LAST + 1)]
    data["crucifixion_year"]["nisan_14"] = rows
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    def show(m):
        alts = [f"{k.split('_')[0]} {m[k]['weekday']} {m[k]['date']}" for k in ("early_crescent", "late_crescent") if m[k]]
        return f"{m['weekday']} {m['date']}" + (f" ({'; '.join(alts)})" if alts else "")
    for r in rows:
        print(f"AD {r['year']}: {show(r)}; a month later {show(r['second_adar'])}")


if __name__ == "__main__":
    main()
