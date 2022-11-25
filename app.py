from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    url_for,
    request,
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
)
from werkzeug.security import check_password_hash
from logging.config import dictConfig
from abort_error import abort_msg
from sql_connector import *
from data_operate import *
from flask_form import *
from telegram.ext import ExtBot
from datetime import date
import pandas as pd

TG_TOKEN = "5655440966:AAHPZsOA9BoEzlvuYHj9YsxT8NFpQ_Ooz14"
ADMIN_CHAT_ID = "348929573"
bot = ExtBot(TG_TOKEN)

app = Flask(__name__)
app.config["SECRET_KEY"] = "eb4d8c3c0bf6ce2125a91c1b71c3f4f7"

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

# login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "這個帳號不存在，或是密碼錯誤。"

users = get_users()


class LoginUser(UserMixin):
    pass


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@login_manager.user_loader
def load_user(user_login):
    if user_login not in users:
        return

    user = LoginUser()
    user.id = user_login
    return user


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        user_login = request.form["email"]

        if user_login in users and check_password_hash(
            users[user_login]["password"], request.form["password"]
        ):
            print(True)
            user = LoginUser()
            user.id = user_login
            login_user(user)
            return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


# app
@app.route("/", methods=["GET", "POST"])
@login_required
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


@app.route("/<int:trip_id>", methods=["GET", "POST"])
@login_required
def trip(trip_id):
    if trip_id not in get_trip_id():
        return render_template("404.html")

    progress = get_progress(trip_id)
    cancel = get_cancel(trip_id)

    if request.method == "POST":
        if cancel == 0:
            if request.form["progress_button"] == "back":
                update_progress(trip_id, progress, how="back")
            elif request.form["progress_button"] == "next":
                update_progress(trip_id, progress, how="next")
        if progress[3] == 0:
            if request.form["progress_button"] == "cancel":
                update_progress(trip_id, progress, how="cancel")
                cancel = get_cancel(trip_id)
            elif request.form["progress_button"] == "uncancel":
                update_progress(trip_id, progress, how="uncancel")
                cancel = get_cancel(trip_id)

    trip_info = get_trip_info(trip_id)
    crew = get_trip_partner(trip_id)
    parti = get_trip_parti(trip_id)
    expend = get_expenditure_of_trip(trip_id)

    itinerary = get_one_itinerary_spot_quote(trip_id)
    itinerary_title = get_itinerary_title(trip_info[0].itinerary_id)
    accommodation = get_itinerary_accommodation(trip_info[0].itinerary_id)

    is_twd = True if trip_info[0].currency == "TWD" else False

    total_expand, profit = expenditure_summary(expend, trip_info)

    return render_template(
        "trip.html",
        trip_info=trip_info,
        crew=crew,
        parti=parti,
        expend=expend,
        cancel=cancel,
        trip_id=trip_id,
        is_twd=is_twd,
        total_expand=total_expand,
        profit=profit,
        itinerary=itinerary,
        itinerary_title=itinerary_title,
        accommodation=accommodation,
    )


@app.route("/trip-deleted=<int:id>", methods=["GET", "POST"])
@login_required
def trip_deleted(id):

    if request.method == "POST":
        if request.form["progress_button"] == "delete":
            delete_trip(id)
    return render_template("trip_deleted.html")


@app.route("/new-trip", methods=["GET", "POST"])
@login_required
def new_trip():
    brands = get_car_brand_selection()
    pre_form = PreNumberOfCustomer()
    if pre_form.validate_on_submit():
        number_of_tourists = pre_form.pre_num_cus.data

    trip_form = new_trip_form(number_of_tourists)

    return render_template(
        "new_trip.html",
        trip_form=trip_form,
        number_of_tourists=number_of_tourists,
        brands=brands,
    )


@app.route("/new-trip/trip-check", methods=["GET", "POST"])
@login_required
def trip_check():
    form_err = None
    trip_form = new_trip_form(1)
    if trip_form.errors:
        form_err = trip_form.errors
    if trip_form.validate_on_submit():
        insert_new_trip(trip_form)
    trip_id = get_max_trip_id()
    return render_template(
        "trip_check.html",
        form_err=form_err,
        trip_id=trip_id,
    )


@app.route("/edit-trip/<int:trip_id>", methods=["GET", "POST"])
@login_required
def edit_trip(trip_id):
    update_done = False
    num_cus = get_number_of_trip_parti(trip_id)
    brands = get_car_brand_selection()
    trip_info = get_one_trip(trip_id)
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
        update_trip(trip_id, trip_form)
        update_done = True

    return render_template(
        "edit_trip.html",
        trip_form=trip_form,
        trip_info=trip_info,
        num_cus=num_cus,
        update_done=update_done,
        trip_id=trip_id,
        is_twd=is_twd,
        brands=brands,
    )


@app.route("/live-car", methods=["GET", "POST"])
def live_car():
    response_filter = request.get_json("car_brand")
    brand_selection = get_car_selection(brand_id=response_filter["brand"])
    brand_selection = {"cars": brand_selection}
    return jsonify(brand_selection)


@app.route("/trip-quote/<int:trip_id>")
@login_required
def trip_quote(trip_id):

    company = get_one_company(1)
    trip_info = get_trip_info(trip_id)
    crew = get_trip_partner(trip_id)
    parti = get_trip_parti(trip_id)
    itinerary = get_one_itinerary_spot_quote(trip_id)
    itinerary_title = get_itinerary_title(trip_info[0].itinerary_id)
    accommodation = get_itinerary_accommodation(trip_info[0].itinerary_id)
    itinerary_species = get_trip_key_species(trip_id)
    today = date.today()

    return render_template(
        "trip_quote.html",
        company=company,
        trip_id=trip_id,
        trip_info=trip_info,
        crew=crew,
        parti=parti,
        itinerary=itinerary,
        itinerary_title=itinerary_title,
        accommodation=accommodation,
        itinerary_species=itinerary_species,
        today=today,
    )


@app.route("/<int:id>/customer", methods=["GET", "POST"])
@login_required
def customer(id):
    cus_info = get_trip_parti(id, all_info=True)

    return render_template("customer.html", cus_info=cus_info, trip_id=id)


@app.route("/<int:id>/new-customer", methods=["GET", "POST"])
@login_required
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
@login_required
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
@login_required
def customer_deleted(id):
    if request.method == "POST":
        if request.form["delete_buttom"] == "delete":
            trip_id = get_trip_id_of_customer(id)
            delete_customer(id, trip_id)
    return render_template("customer_deleted.html", trip_id=trip_id)


@app.route("/<int:trip_id>/new-expenditure", methods=["GET", "POST"])
@login_required
def new_expenditure(trip_id):
    update_done = False
    exp_form = expenditure_form()
    item_classes = get_item_class_selection()

    if exp_form.validate_on_submit():

        insert_expenditure(exp_form, trip_id=trip_id)
        update_done = True
    return render_template(
        "new_expenditure.html",
        trip_id=trip_id,
        exp_form=exp_form,
        update_done=update_done,
        item_classes=item_classes,
    )


@app.route(
    "/<int:trip_id>/edit-expenditure/<int:expenditure_id>", methods=["GET", "POST"]
)
@login_required
def edit_expenditure(trip_id, expenditure_id):
    update_done = False
    item_classes = get_item_class_selection()
    exp_info = get_one_expenditure(expenditure_id)
    exp_form = expenditure_form(
        item_def=exp_info.item_id,
        advancer_def=exp_info.advancer,
        receipt_def=exp_info.receipt,
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
        item_classes=item_classes,
    )


@app.route("/live-item-class", methods=["GET", "POST"])
@login_required
def live_item_class():
    response_filter = request.get_json("item_class")
    item_class_selection = get_item_selection(
        item_class_id=int(response_filter["item_class"])
    )
    item_class_selection = {"item_class": item_class_selection}
    return jsonify(item_class_selection)


@app.route(
    "/<int:trip_id>/expenditure-deleted=<int:expenditure_id>", methods=["GET", "POST"]
)
@login_required
def expenditure_deleted(trip_id, expenditure_id):
    if request.method == "POST":
        if request.form["delete_buttom"] == "delete":
            delete_expenditure(expenditure_id)

    return render_template("expenditure_deleted.html", trip_id=trip_id)


@app.route("/partner", methods=["GET", "POST"])
@login_required
def partner():
    partner_form = NewPartnerForm()
    if partner_form.validate_on_submit():
        insert_new_partner(partner_form)

    partners = get_partner()
    return render_template("partner.html", partners=partners)


@app.route("/new-partner", methods=["GET", "POST"])
@login_required
def new_partner():
    partner_form = NewPartnerForm()

    return render_template("new_partner.html", partner_form=partner_form)


@app.route("/edit-partner/<int:id>", methods=["GET", "POST"])
@login_required
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
@login_required
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
@login_required
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
        ch_description_def=spot_edit.ch_description,
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
@login_required
def item():
    items = get_item()
    return render_template("item.html", items=items)


@app.route("/edit-item/<int:item_id>", methods=["POST", "GET"])
@login_required
def edit_item(item_id):
    update_done = False

    item_info = get_item(item_id=item_id)
    form = item_form(item_class_def=item_info[0].item_class_id)

    if form.validate_on_submit():
        update_item(item_id, form)
        update_done = True

    return render_template(
        "edit_item.html",
        update_done=update_done,
        form=form,
        item_info=item_info,
    )


@app.route("/new-item", methods=["POST", "GET"])
@login_required
def new_item():
    update_done = False
    form = item_form()
    if form.validate_on_submit():
        insert_item(form)
        update_done = True

    return render_template("new_item.html", form=form, update_done=update_done)


@app.route("/itinerary")
@login_required
def itinerary():
    itineraries = get_itinerary_info()
    return render_template("itinerary.html", itineraries=itineraries)


@app.route("/itinerary/<int:itin_id>", methods=["GET", "POST"])
@login_required
def itinerary_info(itin_id):
    update_done = False
    itin = get_one_itinerary_spot(itin_id)
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
@login_required
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
            spots = request.form.getlist("spot_id")
            new_itinerary_dict = organize_itinerary_to_dict(
                spots,
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
@login_required
def live_spot():
    response_filter = request.get_json("live_spot")
    filted_spot_table = filt_spot_by_type_county(spot_for_live, response_filter)
    return jsonify(filted_spot_table)


@app.route("/live-accommodation", methods=["GET", "POST"])
@login_required
def live_accommodation():
    response_filter = request.get_json("live-accommodation")
    filted_accommodation = filt_accommodation_by_county(
        accommodation_for_live, response_filter
    )
    return jsonify(filted_accommodation)


@app.route("/edit-itinerary/<int:itin_id>", methods=["GET", "POST"])
@login_required
def edit_itinerary(itin_id):
    global spot_for_live, accommodation_for_live

    inserted = False
    if request.method == "POST":
        if request.form["submit_buttom"] == "update_itinerary":
            english_title = request.form.get("english_title")
            chinese_title = request.form.get("chinese_title")
            print(request.form.getlist("spot_id"))
            print(request.form.getlist("number_of_schedule"))
            print(request.form.getlist("accommodation_id"))
            new_itinerary_dict = organize_itinerary_to_dict(
                request.form.getlist("spot_id"),
                request.form.getlist("number_of_schedule"),
                request.form.getlist("accommodation_id"),
                english_title=english_title,
                chinese_title=chinese_title,
            )
            update_an_itinerary(itin_id, new_itinerary_dict)
            inserted = True

    spot_for_live = get_spot()
    accommodation_for_live = get_accommodation_live()
    spot_type_selction = get_spot_type_selection()
    county_selction = get_county_selection()

    title = get_itinerary_title(itin_id)
    itineraries, accommodations = get_one_itinerary_for_edit(itin_id)

    itin = organize_query_itinerary_to_dict(
        itineraries,
        accommodations,
        english_title=title.title,
        chinese_title=title.ch_title,
    )

    return render_template(
        "edit_itinerary.html",
        itin_id=itin_id,
        inserted=inserted,
        itin=itin,
        title=title,
        spot_type_selction=spot_type_selction,
        county_selction=county_selction,
    )


@app.route("/spot")
@login_required
def spot():
    spots = classify_spot(get_spot_with_tpye_county())
    return render_template("spot.html", spots=spots)


@app.route("/new-spot", methods=["GET", "POST"])
@login_required
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
@login_required
def spot_info(spot_id):
    onespot = get_one_spot_spottype_county(spot_id)
    species = get_spot_species(spot_id)
    num_sp = len(species)

    app.logger.error(onespot[0].description)

    return render_template(
        "spot_info.html",
        onespot=onespot,
        species=species,
        num_sp=num_sp,
        spot_id=spot_id,
    )


@app.route("/spot/select-species/<int:spot_id>", methods=["GET", "POST"])
@login_required
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
@login_required
def accommodation():
    accomm = classify_accommodation(get_accommodation_with_county())
    return render_template("accommodation.html", accomm=accomm)


@app.route("/edit-accommodation/<int:accommodation_id>", methods=["GET", "POST"])
@login_required
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
@login_required
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
@login_required
def key_species():
    species = get_species()
    return render_template("key_species.html", species=species)


@app.route("/car", methods=["GET", "POST"])
@login_required
def car():
    if request.method == "POST":
        delete_car(int(request.form["car_id"]))
    cars = get_car()
    return render_template("car.html", cars=cars)


@app.route("/new-car", methods=["GET", "POST"])
@login_required
def new_car():
    inserted = False
    form = car_form()

    if form.validate_on_submit():
        insert_car(form)
        inserted = True
        return redirect(url_for("car"))

    return render_template("new_car.html", form=form, inserted=inserted)


@app.route("/admin-cost", methods=["GET", "POST"])
def admin_cost():

    if request.method == "POST":
        if request.form["admin_operate"] == "select_all":
            admin_costs = get_admin_cost(limit=9999)
        else:
            delete_expenditure(int(request.form["admin_operate"]))
    admin_costs = get_admin_cost()

    return render_template("admin_cost.html", admin_costs=admin_costs)


@app.route("/new-admin-cost", methods=["GET", "POST"])
def new_admin_cost():
    inserted = False
    form = expenditure_form()
    item_classes = get_item_class_selection()

    if form.validate_on_submit():
        insert_expenditure(form)
        inserted = True
        return redirect(url_for("admin_cost"))

    return render_template(
        "new_admin_cost.html",
        inserted=inserted,
        item_classes=item_classes,
        form=form,
    )


@app.errorhandler(404)
@login_required
def page_not_found(e):
    return render_template("404.html", err=e), 404


@app.errorhandler(Exception)
def internal_error(error):
    bot.send_message(ADMIN_CHAT_ID, text=abort_msg(error))
    return render_template("error.html", error=error)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
