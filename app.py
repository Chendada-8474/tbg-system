from flask import Flask, jsonify, render_template, request
from sql_connector import *
from data_operate import *
from flask_form import *


app = Flask(__name__)
app.config["SECRET_KEY"] = "tbg"


@app.route("/", methods=["GET", "POST"])
def index():
    limit = 20
    all_trip_count = get_all_trip_count()
    unshown = all_trip_count - limit if all_trip_count > limit else 0

    if request.method == "POST":
        if request.form["all_button"] == "select_all":
            trip = get_index_table(limit=9999)
            unshown = 0
    else:
        trip = get_index_table(limit=limit)

    pre_form = PreNumberOfCustomer()
    return render_template("index.html", trip=trip, pre_form=pre_form, unshown=unshown)


@app.route("/<int:id>", methods=["GET", "POST"])
def trip(id):

    if id not in get_trip_id():
        return render_template("404.html")

    progress = get_progress(id)
    cancel = get_cancel(id)

    if request.method == "POST":
        if cancel == 0:
            if request.form["progress_button"] == "back":
                update_progress(id, progress, how="back")
            elif request.form["progress_button"] == "next":
                update_progress(id, progress, how="next")
        if progress[3] == 0:
            if request.form["progress_button"] == "cancel":
                update_progress(id, progress, how="cancel")
                cancel = get_cancel(id)
            elif request.form["progress_button"] == "uncancel":
                update_progress(id, progress, how="uncancel")
                cancel = get_cancel(id)

    trip_info = get_trip_info(id)
    crew = get_trip_partner(id)
    parti = get_trip_parti(id)
    expend = get_expenditure_of_trip(id)

    is_twd = True if trip_info[0][0].currency == "TWD" else False

    total_expand, profit = expenditure_summary(expend, trip_info)

    return render_template(
        "trip.html",
        trip_info=trip_info,
        crew=crew,
        parti=parti,
        expend=expend,
        cancel=cancel,
        trip_id=id,
        is_twd=is_twd,
        total_expand=total_expand,
        profit=profit,
    )


@app.route("/trip-deleted=<int:id>", methods=["GET", "POST"])
def trip_deleted(id):
    if request.method == "POST":
        if request.form["progress_button"] == "delete":
            delete_trip(id)
    return render_template("trip_deleted.html")


@app.route("/new-trip", methods=["GET", "POST"])
def new_trip():

    pre_form = PreNumberOfCustomer()
    if pre_form.validate_on_submit():
        number_of_tourists = pre_form.pre_num_cus.data

    trip_form = new_trip_form(number_of_tourists)

    return render_template(
        "new_trip.html", trip_form=trip_form, number_of_tourists=number_of_tourists
    )


@app.route("/new-trip/trip-check", methods=["GET", "POST"])
def trip_check():
    form_err = None
    trip_form = new_trip_form(1)
    if trip_form.errors:
        form_err = trip_form.errors
    if trip_form.validate_on_submit():
        insert_new_trip(trip_form)
    trip_id = get_max_trip_id()
    return render_template("trip_check.html", form_err=form_err, trip_id=trip_id)


@app.route("/edit-trip/<int:id>", methods=["GET", "POST"])
def edit_trip(id):
    update_done = False
    num_cus = get_number_of_trip_parti(id)
    trip_info = get_one_trip(id)
    trip_form = update_trip_form(
        currency_def=trip_info.currency,
        account_def=trip_info.receiving_account,
        vehicle_def=trip_info.vehicle,
        guide_def=trip_info.guide,
        driver_def=trip_info.driver,
        manager_def=trip_info.manager,
        sales_def=trip_info.sales,
        accountant_def=trip_info.accountant,
        route_control_def=trip_info.route_control,
        itinerary_def=trip_info.itinerary_id,
    )

    is_twd = True if trip_info.currency == "TWD" else False

    if trip_form.validate_on_submit():
        update_trip(id, trip_form)
        update_done = True

    return render_template(
        "edit_trip.html",
        trip_form=trip_form,
        trip_info=trip_info,
        num_cus=num_cus,
        update_done=update_done,
        trip_id=id,
        is_twd=is_twd,
    )


@app.route("/<int:id>/customer", methods=["GET", "POST"])
def customer(id):
    cus_info = get_trip_parti(id, all_info=True)

    return render_template("customer.html", cus_info=cus_info, trip_id=id)


@app.route("/<int:id>/new-customer", methods=["GET", "POST"])
def new_customer(id):
    cus_form = update_customer_form(country_def=232)
    if cus_form.validate_on_submit():
        insert_customer(cus_form, id)

    return render_template(
        "new_customer.html",
        cus_form=cus_form,
        trip_id=id,
    )


@app.route("/<int:id>/customer-inserted", methods=["GET", "POST"])
def customer_inserted(id):
    form_err = None
    cus_form = update_customer_form()
    if cus_form.validate_on_submit():
        insert_customer(cus_form, id)
    if cus_form.errors:
        form_err = cus_form.errors

    return render_template(
        "customer_inserted.html",
        cus_form=cus_form,
        form_err=form_err,
        trip_id=id,
    )


@app.route("/customer-deleted=<int:id>", methods=["GET", "POST"])
def customer_deleted(id):
    if request.method == "POST":
        if request.form["delete_buttom"] == "delete":
            trip_id = get_trip_id_of_customer(id)
            delete_customer(id, trip_id)
    return render_template("customer_deleted.html", trip_id=trip_id)


@app.route("/<int:id>/new-expenditure", methods=["GET", "POST"])
def new_expenditure(id):
    update_done = False
    exp_form = expenditure_form()
    if exp_form.validate_on_submit():
        insert_expenditure(exp_form, id)
        update_done = True
    return render_template(
        "new_expenditure.html", trip_id=id, exp_form=exp_form, update_done=update_done
    )


@app.route(
    "/<int:trip_id>/edit-expenditure/<int:expenditure_id>", methods=["GET", "POST"]
)
def edit_expenditure(trip_id, expenditure_id):
    update_done = False
    exp_info = get_one_expenditure(expenditure_id)
    exp_form = expenditure_form(
        item_def=exp_info.item_id, advancer_def=exp_info.advancer
    )
    if exp_form.validate_on_submit():
        update_expenditure(expenditure_id, exp_form)
        update_done = True

    return render_template(
        "edit_expenditure.html",
        trip_id=trip_id,
        expenditure_id=expenditure_id,
        exp_info=exp_info,
        exp_form=exp_form,
        update_done=update_done,
    )


@app.route(
    "/<int:trip_id>/expenditure-deleted=<int:expenditure_id>", methods=["GET", "POST"]
)
def expenditure_deleted(trip_id, expenditure_id):
    if request.method == "POST":
        if request.form["delete_buttom"] == "delete":
            delete_expenditure(expenditure_id)

    return render_template("expenditure_deleted.html", trip_id=trip_id)


@app.route("/partner", methods=["GET", "POST"])
def partner():
    partner_form = NewPartnerForm()
    if partner_form.validate_on_submit():
        insert_new_partner(partner_form)

    partners = get_partner()
    return render_template("partner.html", partners=partners)


@app.route("/new-partner", methods=["GET", "POST"])
def new_partner():
    partner_form = NewPartnerForm()

    return render_template("new_partner.html", partner_form=partner_form)


@app.route("/edit-partner/<int:id>", methods=["GET", "POST"])
def edit_partner(id):
    update_done = False
    partner_edit = get_one_partner(id)
    partner_form = NewPartnerForm()

    if partner_form.validate_on_submit():
        update_partner(id, partner_form)
        update_done = True
    return render_template(
        "edit_partner.html",
        partner_form=partner_form,
        partner_edit=partner_edit,
        update_done=update_done,
    )


@app.route("/edit-customer/<int:id>", methods=["GET", "POST"])
def edit_customer(id):

    update_done = False
    cus_info = get_one_customer(id)
    trip_id = get_trip_id_of_customer(id)
    cus_form = update_customer_form(
        gender_def=cus_info.gender, country_def=cus_info.country, note_def=cus_info.note
    )
    if cus_form.validate_on_submit():
        update_customer(id, cus_form)
        update_done = True

    return render_template(
        "edit_customer.html",
        cus_form=cus_form,
        trip_id=trip_id,
        cus_info=cus_info,
        update_done=update_done,
    )


@app.route("/edit-spot/<int:spot_id>", methods=["GET", "POST"])
def edit_spot(spot_id):
    update_done = False
    spot_edit = get_one_spot(spot_id)

    winter = int_booleaner(spot_edit.winter)
    spring = int_booleaner(spot_edit.spring)
    summer = int_booleaner(spot_edit.summer)
    autumn = int_booleaner(spot_edit.autumn)

    onespot_form = spot_form(
        spot_type_def=spot_edit.spot_type_id,
        county_def=spot_edit.county_id,
        description_def=spot_edit.description,
        winter_def=winter,
        spring_def=spring,
        summer_def=summer,
        autumn_def=autumn,
    )

    if onespot_form.validate_on_submit():
        update_spot(spot_id, onespot_form)
        update_done = True

    return render_template(
        "edit_spot.html",
        onespot_form=onespot_form,
        spot_edit=spot_edit,
        update_done=update_done,
        spot_id=spot_id,
    )


@app.route("/item")
def item():
    items = get_item()
    return render_template("item.html", items=items)


@app.route("/itinerary")
def itinerary():
    itineraries = get_itinerary_info()
    return render_template("itinerary.html", itineraries=itineraries)


@app.route("/itinerary/<int:itin_id>", methods=["GET", "POST"])
def itinerary_info(itin_id):
    update_done = False
    itin = get_one_itinerary(itin_id)
    itin_title = get_itinerary_title(itin_id)
    accom = get_itinerary_accommodation(itin_id)

    if request.method == "POST":
        if request.form["invalid_itinerary"] == "invalid_button":
            invalid_itinerary(itin_id)
            update_done = True

    return render_template(
        "itinerary_info.html",
        itin=itin,
        itin_id=itin_id,
        itin_title=itin_title,
        accom=accom,
        update_done=update_done,
    )


@app.route("/new-itinerary", methods=["GET", "POST"])
def new_itinerary():
    global spot_for_live, accommodation_for_live
    spot_for_live = get_spot()
    accommodation_for_live = get_accommodation_live()
    spot_type_selction = get_spot_type_selection()
    county_selction = get_county_selection()
    inserted = False
    itinerary_id = None

    if request.method == "POST":
        if request.form["submit_buttom"] == "new_itinerary":
            english_title = request.form.get("english_title")
            chinese_title = request.form.get("chinese_title")
            new_itinerary_dict = organize_itinerary_to_dict(
                request.form.getlist("spot_id"),
                request.form.getlist("number_of_schedule"),
                request.form.getlist("accommodation_id"),
                english_title=english_title,
                chinese_title=chinese_title,
            )
            insert_an_itinerary(new_itinerary_dict)
            itinerary_id = get_max_trip_id()
            inserted = True

    return render_template(
        "new_itinerary.html",
        spot_type_selction=spot_type_selction,
        county_selction=county_selction,
        inserted=inserted,
        itinerary_id=itinerary_id,
    )


@app.route("/live-spot", methods=["GET", "POST"])
def live_spot():
    response_filter = request.get_json("live_spot")
    filted_spot_table = filt_spot_by_type_county(spot_for_live, response_filter)
    return jsonify(filted_spot_table)


@app.route("/live-accommodation", methods=["GET", "POST"])
def live_accommodation():
    response_filter = request.get_json("live-accommodation")
    filted_accommodation = filt_accommodation_by_county(
        accommodation_for_live, response_filter
    )
    return jsonify(filted_accommodation)


@app.route("/spot")
def spot():
    spots = classify_spot(get_spot_with_tpye_county())
    return render_template("spot.html", spots=spots)


@app.route("/new-spot", methods=["GET", "POST"])
def new_spot():
    update_done = False
    onespot_form = spot_form()
    spot_id = None
    if onespot_form.validate_on_submit():
        insert_spot(onespot_form)
        spot_id = get_max_spot_id()
        update_done = True

    return render_template(
        "new_spot.html",
        onespot_form=onespot_form,
        update_done=update_done,
        spot_id=spot_id,
    )


@app.route("/spot/<int:spot_id>")
def spot_info(spot_id):
    onespot = get_one_spot_spottype_county(spot_id)
    species = get_spot_species(spot_id)
    num_sp = len(species)
    return render_template(
        "spot_info.html",
        onespot=onespot,
        species=species,
        num_sp=num_sp,
        spot_id=spot_id,
    )


@app.route("/spot/select-species/<int:spot_id>", methods=["GET", "POST"])
def select_species(spot_id):

    update_done = False
    species = key_species_spot_or_not(spot_id)
    spot_title = get_spot_title(spot_id)

    if request.method == "POST":
        if request.form["update_button"] == "update_key_species":
            is_key_speices = request.form.getlist("is_key_species")
            update_spot_key_spcies(spot_id, is_key_speices)
            update_done = True

    return render_template(
        "select_species.html",
        species=species,
        spot_id=spot_id,
        spot_title=spot_title,
        update_done=update_done,
    )


@app.route("/accommodation")
def accommodation():
    accomm = classify_accommodation(get_accommodation_with_county())
    return render_template("accommodation.html", accomm=accomm)


@app.route("/edit-accommodation/<int:accommodation_id>", methods=["GET", "POST"])
def edit_accommodation(accommodation_id):
    update_done = False
    accomm_info = get_one_accommodation(accommodation_id)
    accomm_form = accommodation_form(
        county_def=accomm_info.county_id, note_def=accomm_info.note
    )

    if accomm_form.validate_on_submit():
        update_accommodation(accommodation_id, accomm_form)
        update_done = True

    return render_template(
        "edit_accommodation.html",
        accomm_form=accomm_form,
        accomm_info=accomm_info,
        update_done=update_done,
    )


@app.route("/new-accommodation", methods=["GET", "POST"])
def new_accommodation():
    update_done = False
    accomm_form = accommodation_form()
    if accomm_form.validate_on_submit():
        insert_accommodation(accomm_form)
        update_done = True

    return render_template(
        "new_accommodation.html", accomm_form=accomm_form, update_done=update_done
    )


@app.route("/key-species")
def key_species():
    species = get_species()
    return render_template("key_species.html", species=species)


@app.route("/car")
def car():
    cars = get_car()
    return render_template("car.html", cars=cars)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", err=e), 404
