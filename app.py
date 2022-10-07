from flask import Flask, render_template, request
from sql_connector import *
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
    print(exp_form.validate_on_submit())
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


@app.route("/item")
def item():
    items = get_item()
    return render_template("item.html", items=items)


@app.route("/itinerary")
def itinerary():
    return render_template("itinerary.html")


@app.route("/car")
def car():
    cars = get_car()
    return render_template("car.html", cars=cars)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", err=e), 404
