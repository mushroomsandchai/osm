from opening_hours import OpeningHours, State
import datetime
import re
import h3

def get_lat(lat_lon):
    return lat_lon.split(',')[1].rstrip(']')

def get_lon(lat_lon):
    return lat_lon.split(',')[0].lstrip('[')

def h3_res_9(lat, lon):
    return h3.latlng_to_cell(float(lat), float(lon), 9)


def parse_opening_hours(oh_string):
    if not oh_string:
        return None
    
    try:
        # Standard cleaning
        oh_clean = re.sub(r'[–—]', '-', oh_string)
        oh_clean = re.sub(r'\s+', ' ', oh_clean).strip()

        if oh_clean.lower() in ('closed', 'off'):
            return "closed"

        oh = OpeningHours(oh_clean)
        
        if getattr(oh, 'is_24_7', False):
            return "0-24"

        reference_monday = datetime.date(2026, 4, 13)
        all_opens = []
        all_closes = []

        for i in range(7):
            day_date = reference_monday + datetime.timedelta(days=i)
            day_start = datetime.datetime.combine(day_date, datetime.time(0, 0))
            day_end = datetime.datetime.combine(day_date, datetime.time(23, 59))

            for s, e, state, _ in oh.intervals(day_start, day_end):
                if state == State.OPEN:
                    # Capture only the hour
                    all_opens.append(s.hour)
                    all_closes.append(e.hour)

        if not all_opens:
            return "closed"

        start = min(all_opens)
        end = max(all_closes)
        
        return f"{start}-{end}"

    except Exception:
        return None