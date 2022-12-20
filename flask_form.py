from flask_wtf import FlaskForm
from wtforms import Form as BaseForm
from wtforms import (
    StringField,
    IntegerField,
    FloatField,
    TimeField,
    DateField,
    SubmitField,
    SelectField,
    TextAreaField,
    FieldList,
    FormField,
    EmailField,
    BooleanField,
)
from wtforms.validators import DataRequired, NumberRange, Email, Optional
from sql_connector import (
    get_country,
    get_county_selection,
    get_itinerary_selection,
    get_currency_selection,
    get_partner_selection,
    get_spot_type_selection,
    get_car_brand_selection,
    get_car_selection,
    get_bank_selection,
    get_item_selection,
    get_item_class_selection,
)


def customer_form(input_gender="male", country_code=232):
    class CustomerForm(BaseForm):
        first_name = StringField("First Name", validators=[DataRequired()])
        last_name = StringField("Last Name", validators=[DataRequired()])
        gender = SelectField(
            "Gender",
            choices=[("male", "male"), ("female", "female")],
            validators=[DataRequired()],
            default=input_gender,
        )
        phone_number = StringField("Phone Number")
        email = EmailField("Email", validators=[Email(), Optional()])
        birthday = DateField("Birthday", default=None, validators=[Optional()])
        id_number = StringField("ID")
        passport_no = StringField("Passport No.")
        address = StringField("Address")
        country = SelectField(
            "Country",
            choices=[
                (i.country_id, "%s (%s)" % (i.country_name, i.country_code))
                for i in get_country()
            ],
            validators=[DataRequired()],
            default=country_code,
        )
        customer_note = TextAreaField("Note")

    return CustomerForm()


class CustomerForm(BaseForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    gender = SelectField(
        "Gender",
        choices=[("male", "male"), ("female", "female")],
        validators=[DataRequired()],
    )
    phone_number = StringField("Phone Number")
    email = EmailField("Email", validators=[Email(), Optional()])
    birthday = DateField("Birthday", default=None, validators=[Optional()])
    id_number = StringField("ID")
    passport_no = StringField("Passport No.")
    address = StringField("Address")
    country = SelectField(
        "Country",
        choices=[
            (i.country_id, "%s (%s)" % (i.country_name, i.country_code))
            for i in get_country()
        ],
        validators=[DataRequired()],
        default=232,
    )
    customer_note = TextAreaField("Note")


def new_trip_form(num_cus):

    partners = get_partner_selection()

    cars = get_car_selection()

    banks = []
    for b in get_bank_selection():
        if b[3] == 1:
            banks.append((b[0], "%s %s (外幣)" % (b[1], b[2])))
        else:
            banks.append((b[0], "%s %s (台幣)" % (b[1], b[2])))

    currencies = [(i[0], "%s %s" % (i[0], i[1])) for i in get_currency_selection()]
    itineraries = get_itinerary_selection()

    class NewTripForm(FlaskForm):

        # Basic Information
        starting_date = DateField("Begin Date", validators=[DataRequired()])
        number_of_days = IntegerField(
            "Number of Days", validators=[NumberRange(min=1, max=20), DataRequired()]
        )
        cost = FloatField("Cost", validators=[NumberRange(min=0), DataRequired()])
        deposit_amount = FloatField("Deposit", validators=[NumberRange(min=0)])
        deposit_date = DateField(
            "Deposit Date", validators=[Optional(strip_whitespace=True)]
        )
        currency = SelectField(
            "Currency",
            choices=currencies,
            validate_choice=[DataRequired()],
            default="USD",
        )
        pick_up_time = TimeField("Pick up Time", default=None, validators=[Optional()])
        # pick_up_time = TimeField("Pick up time", default=None)
        pick_up_location = StringField("Pick up Location")
        end_time = TimeField("End Time", validators=[Optional(strip_whitespace=True)])
        end_location = StringField("End Location")
        vehicle = SelectField("Car", choices=cars)
        ebird_trip_id = IntegerField("eBird Trip ID")
        itinerary_id = SelectField("Itinerary", choices=itineraries)
        note = TextAreaField("Note")

        # # Rooms
        single_room = IntegerField(
            "Single Room",
            default=0,
            validators=[NumberRange(min=0, max=20)],
        )
        twin_room = IntegerField(
            "Twin Room", default=0, validators=[NumberRange(min=0, max=20)]
        )
        double_room = IntegerField(
            "Double Room", default=0, validators=[NumberRange(min=0, max=20)]
        )
        triple_room = IntegerField(
            "Triple Room", default=0, validators=[NumberRange(min=0, max=20)]
        )
        quadruple_room = IntegerField(
            "Quadruple Room", default=0, validators=[NumberRange(min=0, max=20)]
        )
        other_room = IntegerField(
            "Other Room", default=0, validators=[NumberRange(min=0, max=20)]
        )

        # Bank
        receiving_account = SelectField(
            "Receiving Bank Account", choices=banks, validators=[DataRequired()]
        )

        # TBG partner
        guide = SelectField("Guide", choices=partners)
        driver = SelectField("Driver", choices=partners)
        manager = SelectField("Manager", choices=partners, validators=[DataRequired()])
        sales = SelectField("Sales", choices=partners, validators=[DataRequired()])
        accountant = SelectField(
            "Accountant", choices=partners, validators=[DataRequired()]
        )
        route_control = SelectField(
            "Route Control", choices=partners, validators=[DataRequired()]
        )

        # Main Customer

        create = SubmitField("Create")
        update = SubmitField("儲存變更")

        customers = FieldList(FormField(CustomerForm), min_entries=num_cus)

    return NewTripForm()


def update_trip_form(
    currency_def="USD",
    account_def=2,
    vehicle_def=1,
    guide_def=1,
    driver_def=1,
    manager_def=1,
    sales_def=1,
    accountant_def=3,
    route_control_def=1,
    itinerary_def=0,
):

    partners = get_partner_selection()

    cars = get_car_selection()

    banks = []
    for b in get_bank_selection():
        if b[3] == 1:
            banks.append((b[0], "%s %s (外幣)" % (b[1], b[2])))
        else:
            banks.append((b[0], "%s %s (台幣)" % (b[1], b[2])))

    currencies = [(i[0], "%s %s" % (i[0], i[1])) for i in get_currency_selection()]
    itineraries = get_itinerary_selection()

    class UpdateTripForm(FlaskForm):

        starting_date = DateField("Begin Date", validators=[DataRequired()])
        number_of_days = IntegerField(
            "Number of Days", validators=[NumberRange(min=1, max=20), DataRequired()]
        )
        cost = FloatField("Cost", validators=[NumberRange(min=0), DataRequired()])
        deposit_amount = FloatField("Deposit", validators=[NumberRange(min=0)])
        deposit_date = DateField(
            "Deposit Date", validators=[Optional(strip_whitespace=True)]
        )
        currency = SelectField(
            "Currency",
            choices=currencies,
            validate_choice=[DataRequired()],
            default=currency_def,
        )
        exchange_rate = FloatField(
            "Exchange Rate",
            validators=[NumberRange(min=0), Optional(strip_whitespace=True)],
        )
        pick_up_time = TimeField(
            "Pick up Time",
            validators=[Optional()],
        )
        # pick_up_time = TimeField("Pick up time", default=None)
        pick_up_location = StringField("Pick up Location")
        end_time = TimeField("End Time", validators=[Optional(strip_whitespace=True)])
        end_location = StringField("End Location")
        receiving_account = SelectField(
            "Receiving Bank Account",
            choices=banks,
            validators=[DataRequired()],
            default=account_def,
        )
        vehicle = SelectField("Car", choices=cars, default=vehicle_def)
        ebird_trip_id = IntegerField("eBird Trip ID", validators=[Optional()])
        itinerary_id = SelectField(
            "Itinerary",
            choices=itineraries,
            default=itinerary_def,
            validators=[Optional(strip_whitespace=True)],
        )
        note = TextAreaField("Note")

        guide = SelectField("Guide", choices=partners, default=guide_def)
        driver = SelectField("Driver", choices=partners, default=driver_def)
        manager = SelectField(
            "Manager",
            choices=partners,
            validators=[DataRequired()],
            default=manager_def,
        )
        sales = SelectField(
            "Sales",
            choices=partners,
            validators=[DataRequired()],
            default=sales_def,
        )
        accountant = SelectField(
            "Accountant",
            choices=partners,
            validators=[DataRequired()],
            default=accountant_def,
        )
        route_control = SelectField(
            "Route Control",
            choices=partners,
            validators=[DataRequired()],
            default=route_control_def,
        )

        single_room = IntegerField(
            "Single Room",
            default=0,
            validators=[NumberRange(min=0, max=20)],
        )
        twin_room = IntegerField(
            "Twin Room", default=0, validators=[NumberRange(min=0, max=20)]
        )
        double_room = IntegerField(
            "Double Room", default=0, validators=[NumberRange(min=0, max=20)]
        )
        triple_room = IntegerField(
            "Triple Room", default=0, validators=[NumberRange(min=0, max=20)]
        )
        quadruple_room = IntegerField(
            "Quadruple Room", default=0, validators=[NumberRange(min=0, max=20)]
        )
        other_room = IntegerField(
            "Other Room", default=0, validators=[NumberRange(min=0, max=20)]
        )

        update_trip = SubmitField("儲存變更")

    return UpdateTripForm()


class PreNumberOfCustomer(FlaskForm):
    pre_num_cus = IntegerField(
        "請先輸入團員的數量", validators=[NumberRange(min=1, max=50), DataRequired()]
    )
    start_new_trip = SubmitField("開始新增行程")


class NewPartnerForm(FlaskForm):
    first_name = StringField("First Name (Romanization)", validators=[DataRequired()])
    last_name = StringField("Last Name (Romanization)", validators=[DataRequired()])
    en_first_name = StringField("English Name")
    ch_first_name = StringField("Chinese First Name", validators=[DataRequired()])
    ch_last_name = StringField("Chinese Last Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    email = StringField("Email")
    birthday = DateField("Birthday", validators=[DataRequired()])
    id_number = StringField("ID Number", validators=[DataRequired()])
    zip_code = StringField("Zip Code", validators=[DataRequired()])
    current_address = StringField("Address", validators=[DataRequired()])
    gdrive_url = StringField("Google Drive Url")
    add_partner = SubmitField("新增成員")
    update_partner = SubmitField("儲存變更")


def update_customer_form(gender_def=None, country_def=None, note_def=""):
    class CustomerForm(FlaskForm):
        first_name = StringField("First Name", validators=[DataRequired()])
        last_name = StringField("Last Name", validators=[DataRequired()])
        gender = SelectField(
            "Gender",
            choices=[("male", "male"), ("female", "female")],
            validators=[DataRequired()],
            default=gender_def,
        )
        phone_number = StringField("Phone Number")
        email = EmailField("Email", validators=[Email(), Optional()])
        birthday = DateField("Birthday", validators=[Optional()])
        id_number = StringField("ID")
        passport_no = StringField("Passport No.")
        address = StringField("Address")
        country = SelectField(
            "Country",
            choices=[
                (i.country_id, "%s (%s)" % (i.country_name, i.country_code))
                for i in get_country()
            ],
            validators=[DataRequired()],
            default=country_def,
        )
        note = TextAreaField("Note", default=note_def)
        update_cus = SubmitField("儲存變更")
        create_cus = SubmitField("新增")

    return CustomerForm()


def item_form(item_class_def=None):

    item_classes = get_item_class_selection()

    class ItemForm(FlaskForm):
        item_name = StringField("支出項目名稱", validators=[DataRequired()])
        unit = StringField("單位", validators=[Optional(strip_whitespace=True)])
        default_unit_price = IntegerField(
            "預設單價",
            validators=[
                NumberRange(min=1, max=999999),
                Optional(strip_whitespace=True),
            ],
        )
        item_class_id = SelectField(
            "項目類型", choices=item_classes, default=item_class_def
        )
        create_button = SubmitField("新增")
        update_button = SubmitField("更新資訊")

    return ItemForm()


def expenditure_form(
    item_def=None,
    advancer_def=None,
    receipt_def=False,
):
    items = get_item_selection()
    partner = get_partner_selection()
    partner.insert(0, ("", "-- 代墊人 --"))

    class ExpenditureForm(FlaskForm):
        item_id = SelectField("支出項目", choices=items, default=item_def)
        unit_price = FloatField("單價", validators=[DataRequired()])
        quantity = IntegerField("數量", validators=[DataRequired(), NumberRange(min=1)])
        date = DateField("日期", validators=[DataRequired()])
        advancer = SelectField(
            "代墊人",
            choices=partner,
            default=advancer_def,
            validators=[Optional(strip_whitespace=True)],
        )
        receipt = BooleanField("收據", default=receipt_def)
        note = StringField("備註")
        create_expenditure = SubmitField("新增支出")
        update_expenditure = SubmitField("儲存變更")

    return ExpenditureForm()


def spot_form(
    spot_type_def=1,
    county_def=1,
    description_def=None,
    ch_description_def=None,
    winter_def=False,
    spring_def=False,
    summer_def=False,
    autumn_def=False,
):
    spot_types = get_spot_type_selection()
    counties = get_county_selection()

    class SpotForm(FlaskForm):
        spot_name = StringField("English Spot Name", validators=[DataRequired()])
        spot_ch_name = StringField("Chinese Spot Name", validators=[DataRequired()])
        longitude = FloatField(
            "Longitude", validators=[Optional(strip_whitespace=True)]
        )
        latitude = FloatField("Latitude", validators=[Optional(strip_whitespace=True)])
        description = TextAreaField(
            "Description",
            default=description_def,
            validators=[Optional(strip_whitespace=True)],
        )
        ch_description = TextAreaField(
            "Chinese Description",
            default=ch_description_def,
            validators=[Optional(strip_whitespace=True)],
        )
        county_id = SelectField(
            "County",
            choices=counties,
            default=county_def,
        )
        spot_type_id = SelectField(
            "Spot Type", choices=spot_types, default=spot_type_def
        )
        winter = BooleanField("winter", default=winter_def)
        spring = BooleanField("spring", default=spring_def)
        summer = BooleanField("summer", default=summer_def)
        autumn = BooleanField("autumn", default=autumn_def)

        update_spot = SubmitField("儲存變更")
        create_spot = SubmitField("新增")

    return SpotForm()


def accommodation_form(wifi_def=1, county_def=None, note_def=None):
    counties = get_county_selection()

    class AccommodationForm(FlaskForm):
        accommodation_name = StringField("English Name", validators=[DataRequired()])
        accommodation_ch_name = StringField("Chinese Name", validators=[DataRequired()])
        address = StringField("English Address", validators=[DataRequired()])
        ch_address = StringField("Chinese Address", validators=[DataRequired()])
        phone_number = StringField("Phone Number", validators=[DataRequired()])
        wifi = BooleanField("WIFI", default=wifi_def)
        county_id = SelectField("County", choices=counties, default=county_def)
        elevation = IntegerField(
            "Elevation",
            validators=[NumberRange(min=0, max=4000), Optional(strip_whitespace=True)],
        )
        note = TextAreaField(
            "Note", default=note_def, validators=[Optional(strip_whitespace=True)]
        )
        update_accommodation = SubmitField("儲存變更")
        create_accommodation = SubmitField("新增")

    return AccommodationForm()


def car_form(car_brand_def=None):

    car_brand_selection = get_car_brand_selection()

    class CarForm(FlaskForm):
        model = StringField("Model Name", validators=[DataRequired()])
        car_brand_id = SelectField(
            "Brand",
            choices=car_brand_selection,
            validators=[DataRequired()],
            default=car_brand_def,
        )
        seat = IntegerField(
            "No. of Seat",
            validators=[DataRequired(), NumberRange(min=2, max=50)],
        )
        create_car = SubmitField("新增車輛")

    return CarForm()
