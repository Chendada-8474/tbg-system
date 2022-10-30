def expenditure_summary(exp_info, trip_info):
    total_expend = 0

    try:
        for i in exp_info:
            total_expend += i[0].unit_price * i[0].quantity
        profit = trip_info[0].cost * trip_info[0].exchange_rate - total_expend
        profit = round(profit, 0)
    except:
        total_expend = None
        profit = None

    return total_expend, profit


def int_booleaner(bool_int: int):
    return bool_int == 1


def classify_spot(spots):
    # types = get_spot_type()
    classified_spots = {}

    for s in spots:
        if s[1].type not in classified_spots.keys():
            classified_spots[s[1].type] = []
        classified_spots[s[1].type].append(s)

    return classified_spots


def classify_accommodation(accommodations):
    classified_accommodation = {}

    for a in accommodations:
        if a[1].county_ch_name not in classified_accommodation.keys():
            classified_accommodation[a[1].county_ch_name] = []
        classified_accommodation[a[1].county_ch_name].append(a)
    return classified_accommodation


def filt_spot_by_type_county(spots, response_filter: dict):
    selection = []
    is_county_empty = response_filter["county_id"] == ""
    is_spot_type_empty = response_filter["spot_type_id"] == ""

    for s in spots:
        if not is_county_empty:
            is_county = s.county_id == int(response_filter["county_id"])
        else:
            is_county = True

        if not is_spot_type_empty:
            is_spot_type = s.spot_type_id == int(response_filter["spot_type_id"])
        else:
            is_spot_type = True

        if is_county and is_spot_type:
            selection.append((s.spot_id, s.spot_ch_name))
    return selection


def filt_accommodation_by_county(accommodation: list, response_filter):
    selection = []
    for a in accommodation:
        if a[2] == int(response_filter) or a[2] == "":
            selection.append((a[0], a[1]))
    return selection


def organize_itinerary_to_dict(
    spots,
    days,
    accommodations,
    english_title="Untitled Itinerary",
    chinese_title="尚未命名的行程",
):
    print(spots, days, accommodations)
    schedule = []
    for i, d in enumerate(days):
        day_spots = []
        num_days = int(d)
        for n in range(num_days):
            day_spots.append(spots[0])
            spots.pop(0)
        day = {"spots": day_spots, "accommodation": accommodations[i]}
        schedule.append(day)

    itinerary = {
        "title": english_title,
        "ch_title": chinese_title,
        "schedule": schedule,
    }

    return itinerary


def organize_query_itinerary_to_dict(
    itinerary: list, accommodation: list, english_title=None, chinese_title=None
):
    accommodation = iter(accommodation)

    itinerary_org = {
        "title": english_title,
        "ch_title": chinese_title,
        "schedule": [],
    }

    first_day = -1
    schedule_index = 1

    for i in itinerary:

        if first_day != i[0]:
            day_accomm = next(accommodation)
            day = {"spots": [], "accommodation": None}

            # print(day_accomm)

            day["accommodation"] = (day_accomm[1], day_accomm[2])
            itinerary_org["schedule"].append(day)
            first_day = i[0]

        # print(i)
        itinerary_org["schedule"][-1]["spots"].append((schedule_index, i[2], i[3]))

        schedule_index += 1

    return itinerary_org


if __name__ == "__main__":
    from sql_connector import get_one_itinerary_for_edit

    itinerary_info, accommodations = get_one_itinerary_for_edit(6)

    result = organize_query_itinerary_to_dict(
        itinerary_info,
        accommodations,
        english_title="test title",
        chinese_title="這是一個測試標題",
    )

    print(result)
