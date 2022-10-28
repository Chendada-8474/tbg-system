from sqlalchemy import create_engine, desc, case, and_, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import func
from datetime import date


engine = create_engine(
    "mysql+pymysql://root:ro2231031@192.168.1.104:3306/taiwanbirdguide"
)
Base = declarative_base()
Base.metadata.reflect(engine)
db_session = scoped_session(sessionmaker(bind=engine))

TRIP_STATUS_COL = ["to_quote", "deposit", "pay_off", "trip_end", "accounted"]
TRIP_STATUS = ["quote sent", "got deposit", "paid off", "trip finished", "reimbursed"]


class User(Base):
    __table__ = Base.metadata.tables["user"]


class Trip(Base):
    __table__ = Base.metadata.tables["trip"]


class Customer(Base):
    __table__ = Base.metadata.tables["customer"]


class TripCustomer(Base):
    __table__ = Base.metadata.tables["trip_customer"]


class Partner(Base):
    __table__ = Base.metadata.tables["partner"]


class Car(Base):
    __table__ = Base.metadata.tables["car"]


class Expenditure(Base):
    __table__ = Base.metadata.tables["expenditure"]


class Item(Base):
    __table__ = Base.metadata.tables["item"]


class Country(Base):
    __table__ = Base.metadata.tables["country"]


class BankAccount(Base):
    __table__ = Base.metadata.tables["bank_account"]


class Currency(Base):
    __table__ = Base.metadata.tables["currency"]


class Spot(Base):
    __table__ = Base.metadata.tables["spot"]


class SpotType(Base):
    __table__ = Base.metadata.tables["spot_type"]


class KeySpecies(Base):
    __table__ = Base.metadata.tables["key_species"]


class SpeciesSpot(Base):
    __table__ = Base.metadata.tables["species_spot"]


class Accommodation(Base):
    __table__ = Base.metadata.tables["accommodation"]


class Itinerary(Base):
    __table__ = Base.metadata.tables["itinerary"]


class ItineraryTitle(Base):
    __table__ = Base.metadata.tables["itinerary_title"]


class ItineraryAccommodation(Base):
    __table__ = Base.metadata.tables["itinerary_accommodation"]


class County(Base):
    __table__ = Base.metadata.tables["county"]


class Company(Base):
    __table__ = Base.metadata.tables["company"]


def get_one_company(company_id):
    company = db_session.query(Company).filter(Company.company_id == company_id).first()
    return company


def get_index_table(limit=5):
    trip = (
        db_session.query(
            Trip.trip_id,
            Customer.first_name,
            Customer.last_name,
            Trip.starting_date,
            Trip.number_of_days,
            Trip.number_of_tourists,
            Partner.first_name,
            Partner.last_name,
            Country.country_name,
            Trip.accounted,
            Trip.trip_end,
            Trip.pay_off,
            Trip.deposit,
            Trip.to_quote,
            Trip.cancel,
        )
        .join(Customer, Trip.contact_client == Customer.customer_id)
        .join(Partner, Trip.guide == Partner.partner_id)
        .join(Country, Customer.country == Country.country_id)
        .order_by(desc(Trip.starting_date))
        .limit(limit)
        .all()
    )

    index_trip = []
    for t in trip:
        cus_name = "%s %s" % (t[1], t[2])
        gui_name = "%s %s" % (t[6], t[7])
        status = None
        for i, s in enumerate([t[9], t[10], t[11], t[12], t[13]]):
            if s == 1:
                status = list(reversed(TRIP_STATUS))[i]
                break
            else:
                status = "draft"
        index_trip.append(
            (t[0], cus_name, t[3], t[4], t[5], gui_name, t[8], status, t[14])
        )

    return index_trip


def get_all_trip_count():
    count = db_session.query(Trip).count()
    return count


def get_trip_info(id):
    trip_info = (
        db_session.query(Trip, Customer, Car, Country, BankAccount, ItineraryTitle)
        .join(Customer, Trip.contact_client == Customer.customer_id)
        .join(Car, Trip.vehicle == Car.car_id)
        .join(BankAccount, Trip.receiving_account == BankAccount.bank_account_id)
        .join(Country, Customer.country == Country.country_id)
        .outerjoin(ItineraryTitle, Trip.itinerary_id == ItineraryTitle.itinerary_id)
        .filter(Trip.trip_id == id)
        .first()
    )
    return trip_info


def get_one_trip(id):
    trip_info = db_session.query(Trip).filter(Trip.trip_id == id).first()

    return trip_info


def get_trip_partner(id):
    guide = (
        db_session.query(
            Trip.trip_id,
            Partner.first_name,
            Partner.last_name,
            Partner.ch_first_name,
            Partner.ch_last_name,
        )
        .join(Partner, Trip.guide == Partner.partner_id)
        .filter(Trip.trip_id == id)
        .first()
    )
    driver = (
        db_session.query(
            Trip.trip_id,
            Partner.first_name,
            Partner.last_name,
            Partner.ch_first_name,
            Partner.ch_last_name,
        )
        .join(Partner, Trip.driver == Partner.partner_id)
        .filter(Trip.trip_id == id)
        .first()
    )
    manager = (
        db_session.query(Trip.trip_id, Partner.first_name, Partner.last_name)
        .join(Partner, Trip.manager == Partner.partner_id)
        .filter(Trip.trip_id == id)
        .first()
    )
    sales = (
        db_session.query(
            Trip.trip_id,
            Partner.first_name,
            Partner.last_name,
            Partner.email,
            Partner.phone_number,
        )
        .join(Partner, Trip.sales == Partner.partner_id)
        .filter(Trip.trip_id == id)
        .first()
    )
    accountant = (
        db_session.query(Trip.trip_id, Partner.first_name, Partner.last_name)
        .join(Partner, Trip.accountant == Partner.partner_id)
        .filter(Trip.trip_id == id)
        .first()
    )
    route_control = (
        db_session.query(Trip.trip_id, Partner.first_name, Partner.last_name)
        .join(Partner, Trip.route_control == Partner.partner_id)
        .filter(Trip.trip_id == id)
        .first()
    )

    crew = {
        "guide": "%s %s" % (guide[1], guide[2]),
        "guide_ch": "%s %s" % (guide[4], guide[3]),
        "driver": "%s %s" % (driver[1], driver[2]),
        "driver_ch": "%s %s" % (driver[4], driver[3]),
        "manager": "%s %s" % (manager[1], manager[2]),
        "sales": "%s %s" % (sales[1], sales[2]),
        "accountant": "%s %s" % (accountant[1], accountant[2]),
        "route_control": "%s %s" % (route_control[1], route_control[2]),
        "sales_contact": {"email": sales[3], "phone_number": sales[4]},
    }
    return crew


def _count_age(birthday):
    if not birthday:
        return None
    today = date.today()
    return (
        today.year
        - birthday.year
        - ((today.month, today.day) < (birthday.month, birthday.day))
    )


def get_trip_parti(id, all_info=False):
    parti_query = (
        db_session.query(
            TripCustomer.customer_id,
            Customer.first_name,
            Customer.last_name,
            Customer.gender,
            Customer.birthday,
            Country.country_name,
        )
        .join(Customer, TripCustomer.customer_id == Customer.customer_id)
        .join(Country, Customer.country == Country.country_id)
        .filter(TripCustomer.trip_id == id)
        .all()
    )

    if all_info:
        parti_query = (
            db_session.query(Customer, Country)
            .join(TripCustomer, TripCustomer.customer_id == Customer.customer_id)
            .join(Country, Country.country_id == Customer.country)
            .filter(TripCustomer.trip_id == id)
            .all()
        )
        return parti_query

    parti = [
        (p[0], "%s %s" % (p[1], p[2]), p[3], _count_age(p[4]), p[5])
        for p in parti_query
    ]

    return parti


def get_number_of_trip_parti(trip_id):
    rows = (
        db_session.query(TripCustomer).filter(TripCustomer.trip_id == trip_id).count()
    )
    return rows


def get_progress(id):
    progress = (
        db_session.query(
            Trip.to_quote, Trip.deposit, Trip.pay_off, Trip.trip_end, Trip.accounted
        )
        .filter(Trip.trip_id == id)
        .first()
    )

    if not progress:
        return None

    return list(progress)


def get_cancel(id):
    canceled = db_session.query(Trip.cancel).filter(Trip.trip_id == id).first()
    return canceled[0]


def get_item():
    item = db_session.query(Item).all()
    return item


def update_progress(trip_id: int, progress: list, how=None):
    if not how:
        return
    elif how == "next":
        for i, p in enumerate(progress):
            if p == 0:
                db_session.query(Trip).filter(Trip.trip_id == trip_id).update(
                    {TRIP_STATUS_COL[i]: 1}
                )
                update_deposit_date(trip_id, str(date.today()))
                break
    elif how == "back":
        cols = list(reversed(TRIP_STATUS_COL))
        progress.reverse()
        for i, p in enumerate(progress):
            if p == 1:
                db_session.query(Trip).filter(Trip.trip_id == trip_id).update(
                    {cols[i]: 0}
                )
                break
    elif how == "cancel":
        db_session.query(Trip).filter(Trip.trip_id == trip_id).update({"cancel": 1})
    elif how == "uncancel":
        db_session.query(Trip).filter(Trip.trip_id == trip_id).update({"cancel": 0})
    db_session.commit()


def update_deposit_date(trip_id, update_date):
    db_session.query(Trip).filter(Trip.trip_id == trip_id).update(
        {"deposit_date": update_date}
    )
    db_session.commit()


def get_trip_id():
    max_id = db_session.query(Trip.trip_id).all()
    max_id = [i[0] for i in max_id]
    return max_id


def get_partner():
    partner = db_session.query(Partner).all()
    return partner


def get_car():
    cars = db_session.query(Car).all()
    return cars


def get_country():
    countries = db_session.query(Country).all()
    return countries


def get_partner_selection():
    partners = db_session.query(
        Partner.partner_id, Partner.first_name, Partner.last_name
    ).all()
    return partners


def get_bank_selection():
    banks = db_session.query(
        BankAccount.bank_account_id,
        BankAccount.account_name,
        BankAccount.bank_ch_name,
        BankAccount.foreign,
    ).all()
    return banks


def get_currency_selection():
    currencies = db_session.query(
        Currency.currency_code, Currency.currency_ch_name
    ).all()
    return currencies


def get_item_selection():
    items = (
        db_session.query(Item.item_id, Item.item_name).order_by(Item.item_class).all()
    )
    return items


def get_max_cus_id():
    max_id = db_session.query(func.max(Customer.customer_id)).first()[0]
    return max_id


def get_max_trip_id():
    max_id = db_session.query(func.max(Trip.trip_id)).first()[0]
    return max_id


def get_max_spot_id():
    max_id = db_session.query(func.max(Spot.spot_id)).first()[0]
    return max_id


def insert_new_trip(form):

    # insert customers
    parti = []

    for c in form.customers:

        new_cus = Customer(
            first_name=c.first_name.data,
            last_name=c.last_name.data,
            gender=c.gender.data,
            phone_number=c.phone_number.data,
            email=c.email.data,
            birthday=c.birthday.data,
            id_number=c.id_number.data,
            passport_no=c.passport_no.data,
            address=c.address.data,
            country=c.country.data,
            note=c.customer_note.data,
        )
        db_session.add(new_cus)
        db_session.commit()
        parti.append(get_max_cus_id())

    # insert tirp
    new_trip = Trip(
        starting_date=form.starting_date.data,
        number_of_days=form.number_of_days.data,
        number_of_tourists=len(parti),
        cost=form.cost.data,
        deposit_amount=form.deposit_amount.data,
        currency=form.currency.data,
        pick_up_time=form.pick_up_time.data,
        pick_up_location=form.pick_up_location.data,
        end_time=form.end_time.data,
        end_location=form.end_location.data,
        guide=form.guide.data,
        driver=form.driver.data,
        manager=form.manager.data,
        sales=form.sales.data,
        accountant=form.accountant.data,
        route_control=form.route_control.data,
        single_room=form.single_room.data,
        twin_room=form.twin_room.data,
        double_room=form.double_room.data,
        triple_room=form.triple_room.data,
        quadruple_room=form.quadruple_room.data,
        other_room=form.other_room.data,
        vehicle=form.vehicle.data,
        contact_client=parti[0],
        receiving_account=form.receiving_account.data,
        note=form.note.data,
    )
    db_session.add(new_trip)
    db_session.commit()

    # insert trip_customer
    trip_id = get_max_trip_id()
    new_trip_cus = []
    for i in parti:
        new_trip_cus.append(TripCustomer(trip_id=trip_id, customer_id=i))
    db_session.add_all(new_trip_cus)
    db_session.commit()
    return


def delete_trip(trip_id):

    cus_ids_in_trip = (
        db_session.query(TripCustomer.customer_id)
        .filter(TripCustomer.trip_id == trip_id)
        .all()
    )

    cus_ids_in_trip = [i[0] for i in cus_ids_in_trip]

    # delete trip
    db_session.query(Trip).filter(Trip.trip_id == trip_id).delete()
    db_session.commit()

    # detele trip_customer
    db_session.query(TripCustomer).filter(TripCustomer.trip_id == trip_id).delete()
    db_session.commit()

    # delete customer
    db_session.query(Customer).filter(
        Customer.customer_id.in_(cus_ids_in_trip)
    ).delete()
    db_session.commit()


def delete_expenditure(expenditure_id):
    db_session.query(Expenditure).filter(
        Expenditure.expenditure_id == expenditure_id
    ).delete()
    db_session.commit()
    pass


def insert_new_partner(form):
    new_partner = Partner(
        first_name=form.first_name.data,
        last_name=form.last_name.data,
        en_first_name=form.en_first_name.data,
        ch_first_name=form.ch_first_name.data,
        ch_last_name=form.ch_last_name.data,
        phone_number=form.phone_number.data,
        email=form.email.data,
        birthday=form.birthday.data,
        id_number=form.id_number.data,
        zip_code=form.zip_code.data,
        current_address=form.current_address.data,
        gdrive_url=form.gdrive_url.data,
    )
    db_session.add(new_partner)
    db_session.commit()
    return


def update_customer(customer_id, cus_form):

    db_session.query(Customer).filter(Customer.customer_id == customer_id).update(
        {
            "first_name": cus_form.first_name.data,
            "last_name": cus_form.last_name.data,
            "gender": cus_form.gender.data,
            "phone_number": cus_form.phone_number.data,
            "email": cus_form.email.data,
            "birthday": cus_form.birthday.data,
            "id_number": cus_form.id_number.data,
            "passport_no": cus_form.passport_no.data,
            "address": cus_form.address.data,
            "country": cus_form.country.data,
            "note": cus_form.note.data,
        }
    )
    db_session.commit()


def delete_customer(customer_id: int, trip_id: int):
    db_session.query(Customer).filter(Customer.customer_id == customer_id).delete()
    db_session.commit()
    db_session.query(TripCustomer).filter(
        TripCustomer.customer_id == customer_id
    ).delete()
    db_session.commit()

    num_tourist = (
        db_session.query(Trip.number_of_tourists)
        .filter(Trip.trip_id == trip_id)
        .first()
    )[0]
    db_session.query(Trip).filter(Trip.trip_id == trip_id).update(
        {"number_of_tourists": num_tourist - 1}
    )
    db_session.commit()


def insert_customer(cus_form, trip_id: int):
    new_customer = Customer(
        first_name=cus_form.first_name.data,
        last_name=cus_form.last_name.data,
        gender=cus_form.gender.data,
        phone_number=cus_form.phone_number.data,
        email=cus_form.email.data,
        birthday=cus_form.birthday.data,
        id_number=cus_form.id_number.data,
        passport_no=cus_form.passport_no.data,
        address=cus_form.address.data,
        country=cus_form.country.data,
        note=cus_form.note.data,
    )
    db_session.add(new_customer)
    db_session.commit()

    new_trip_customer = TripCustomer(customer_id=get_max_cus_id(), trip_id=trip_id)
    db_session.add(new_trip_customer)
    db_session.commit()

    num_tourist = (
        db_session.query(Trip.number_of_tourists)
        .filter(Trip.trip_id == trip_id)
        .first()
    )[0]
    db_session.query(Trip).filter(Trip.trip_id == trip_id).update(
        {"number_of_tourists": num_tourist + 1}
    )
    db_session.commit()


def update_trip(trip_id, form):
    db_session.query(Trip).filter(Trip.trip_id == trip_id).update(
        {
            "starting_date": form.starting_date.data,
            "number_of_days": form.number_of_days.data,
            "cost": form.cost.data,
            "deposit_amount": form.deposit_amount.data,
            "deposit_date": form.deposit_date.data,
            "currency": form.currency.data,
            "exchange_rate": form.exchange_rate.data,
            "pick_up_time": form.pick_up_time.data,
            "pick_up_location": form.pick_up_location.data,
            "end_location": form.end_location.data,
            "guide": form.guide.data,
            "driver": form.driver.data,
            "manager": form.manager.data,
            "sales": form.sales.data,
            "accountant": form.accountant.data,
            "route_control": form.route_control.data,
            "single_room": form.single_room.data,
            "twin_room": form.twin_room.data,
            "double_room": form.double_room.data,
            "triple_room": form.triple_room.data,
            "quadruple_room": form.quadruple_room.data,
            "other_room": form.other_room.data,
            "vehicle": form.vehicle.data,
            "ebird_trip_id": form.ebird_trip_id.data,
            "receiving_account": form.receiving_account.data,
            "note": form.note.data,
        }
    )
    db_session.commit()


def update_partner(partner_id, form):
    db_session.query(Partner).filter(Partner.partner_id == partner_id).update(
        {
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "en_first_name": form.en_first_name.data,
            "ch_first_name": form.ch_first_name.data,
            "ch_last_name": form.ch_last_name.data,
            "email": form.email.data,
            "birthday": form.birthday.data,
            "id_number": form.id_number.data,
            "zip_code": form.zip_code.data,
            "current_address": form.current_address.data,
            "gdrive_url": form.gdrive_url.data,
            "note": form.note.data,
        }
    )
    db_session.commit()


def update_expenditure(expenditure_id, form):
    if form.advancer.data != "None":
        db_session.query(Expenditure).filter(
            Expenditure.expenditure_id == expenditure_id
        ).update(
            {
                "item_id": form.item_id.data,
                "unit_price": form.unit_price.data,
                "quantity": form.quantity.data,
                "date": form.date.data,
                "note": form.note.data,
                "advancer": form.advancer.data,
            }
        )
    else:
        db_session.query(Expenditure).filter(
            Expenditure.expenditure_id == expenditure_id
        ).update(
            {
                "item_id": form.item_id.data,
                "unit_price": form.unit_price.data,
                "quantity": form.quantity.data,
                "date": form.date.data,
                "note": form.note.data,
            }
        )
    db_session.commit()


def get_one_partner(partner_id: int):
    partner = db_session.query(Partner).filter(Partner.partner_id == partner_id).first()
    return partner


def get_one_customer(customer_id: int):
    customer = (
        db_session.query(Customer).filter(Customer.customer_id == customer_id).first()
    )
    return customer


def get_trip_id_of_customer(customer_id: int):
    trip_id = (
        db_session.query(TripCustomer.trip_id)
        .filter(TripCustomer.customer_id == customer_id)
        .first()
    )[0]
    return trip_id


def get_expenditure_of_trip(trip_id):
    expend = (
        db_session.query(Expenditure, Item, Partner)
        .join(Item, Item.item_id == Expenditure.item_id)
        .outerjoin(Partner, Partner.partner_id == Expenditure.advancer)
        .filter(Expenditure.trip_id == trip_id)
        .all()
    )
    return expend


def get_one_expenditure(expenditure_id):
    expenditure = (
        db_session.query(Expenditure)
        .filter(Expenditure.expenditure_id == expenditure_id)
        .first()
    )
    return expenditure


def insert_expenditure(exp_from, trip_id: int):

    if exp_from.advancer.data != "None":
        new_expenditure = Expenditure(
            trip_id=trip_id,
            item_id=exp_from.item_id.data,
            unit_price=exp_from.unit_price.data,
            quantity=exp_from.quantity.data,
            date=exp_from.date.data,
            note=exp_from.note.data,
            advancer=exp_from.advancer.data,
        )
    else:
        new_expenditure = Expenditure(
            trip_id=trip_id,
            item_id=exp_from.item_id.data,
            unit_price=exp_from.unit_price.data,
            quantity=exp_from.quantity.data,
            date=exp_from.date.data,
            note=exp_from.note.data,
        )

    db_session.add(new_expenditure)
    db_session.commit()


def get_itinerary_info():
    itinerary = (
        db_session.query(ItineraryTitle)
        .order_by(desc(ItineraryTitle.itinerary_id))
        .all()
    )
    return itinerary


def get_one_itinerary_spot(itin_id: int):

    itinerary = (
        db_session.query(Itinerary, Spot)
        .join(Spot, Itinerary.spot_id == Spot.spot_id)
        .join(Trip, Itinerary.itinerary_id == Trip.itinerary_id)
        .filter(Itinerary.itinerary_id == itin_id)
        .all()
    )

    return itinerary


def get_one_itinerary_spot_quote(trip_id: int):
    sql = (
        """
    SELECT itinerary.day, itinerary.schedule, itinerary.spot_id, spot.spot_name, spot_ch_name, spot.description, DATE_ADD(trip.starting_date, INTERVAL itinerary.day DAY) AS "each_date", DAYNAME(DATE_ADD(trip.starting_date, INTERVAL itinerary.day DAY)) AS "day_of_week" FROM taiwanbirdguide.itinerary LEFT JOIN taiwanbirdguide.spot ON itinerary.spot_id = spot.spot_id LEFT JOIN taiwanbirdguide.trip ON trip.itinerary_id = itinerary.itinerary_id WHERE trip.trip_id = %s;
    """
        % trip_id
    )
    itinerary = db_session.execute(sql).fetchall()

    return itinerary


def get_itinerary_title(itin_id: int):
    title = (
        db_session.query(ItineraryTitle)
        .filter(ItineraryTitle.itinerary_id == itin_id)
        .first()
    )
    return title


def get_itinerary_accommodation(itin_id: int):
    accom = (
        db_session.query(ItineraryAccommodation, Accommodation)
        .join(
            Accommodation,
            ItineraryAccommodation.accommodation_id == Accommodation.accommodation_id,
        )
        .filter(ItineraryAccommodation.itinerary_id == itin_id)
        .all()
    )
    return accom


def get_one_itinerary_for_edit(itinerary_id):
    itinerary = (
        db_session.query(
            Itinerary.day,
            Itinerary.schedule,
            Itinerary.spot_id,
            Spot.spot_ch_name,
        )
        .join(Spot, Spot.spot_id == Itinerary.spot_id)
        .filter(Itinerary.itinerary_id == itinerary_id)
        .all()
    )

    accommodation = (
        db_session.query(
            ItineraryAccommodation.day,
            ItineraryAccommodation.accommodation_id,
            Accommodation.accommodation_ch_name,
        )
        .join(
            Accommodation,
            Accommodation.accommodation_id == ItineraryAccommodation.accommodation_id,
        )
        .filter(ItineraryAccommodation.itinerary_id == itinerary_id)
        .all()
    )

    return itinerary, accommodation


def get_spot():
    spot = db_session.query(Spot).all()
    return spot


def get_species():
    species = db_session.query(KeySpecies).all()
    return species


def get_accommodation_with_county():
    accommodation = (
        db_session.query(Accommodation, County)
        .join(County, County.county_id == Accommodation.county_id)
        .all()
    )
    return accommodation


def get_spot_type_selection():
    types = db_session.query(SpotType).all()
    types = [(i.spot_type_id, i.type) for i in types]
    return types


def get_one_spot(spot_id):
    spot = db_session.query(Spot).filter(Spot.spot_id == spot_id).first()
    return spot


def get_one_spot_spottype_county(spot_id):
    spot = (
        db_session.query(Spot, SpotType, County)
        .join(SpotType, SpotType.spot_type_id == Spot.spot_type_id)
        .join(County, County.county_id == Spot.county_id)
        .filter(Spot.spot_id == spot_id)
        .first()
    )
    return spot


def get_spot_type():
    types = db_session.query(SpotType).all()
    return types


def get_spot_with_tpye_county():
    spot = (
        db_session.query(Spot, SpotType, County)
        .join(SpotType, SpotType.spot_type_id == Spot.spot_type_id)
        .join(County, County.county_id == Spot.county_id)
        .all()
    )

    return spot


def get_spot_species(spot_id):
    species = (
        db_session.query(SpeciesSpot, KeySpecies)
        .join(KeySpecies, KeySpecies.key_species_id == SpeciesSpot.key_species_id)
        .filter(SpeciesSpot.spot_id == spot_id)
        .all()
    )
    return species


def update_spot(spot_id, form):
    db_session.query(Spot).filter(Spot.spot_id == spot_id).update(
        {
            "spot_name": form.spot_name.data,
            "spot_ch_name": form.spot_ch_name.data,
            "longitude": form.longitude.data,
            "latitude": form.latitude.data,
            "county_id": form.county_id.data,
            "spot_type_id": form.spot_type_id.data,
            "description": form.description.data,
            "winter": form.winter.data,
            "spring": form.spring.data,
            "summer": form.summer.data,
            "autumn": form.autumn.data,
        }
    )
    db_session.commit()


def insert_spot(form):
    new_spot = Spot(
        spot_name=form.spot_name.data,
        spot_ch_name=form.spot_ch_name.data,
        longitude=form.longitude.data,
        latitude=form.latitude.data,
        county_id=form.county_id.data,
        spot_type_id=form.spot_type_id.data,
        description=form.description.data,
        winter=form.winter.data,
        spring=form.spring.data,
        summer=form.summer.data,
        autumn=form.autumn.data,
    )
    db_session.add(new_spot)
    db_session.commit()


def get_county_selection():
    county = db_session.query(County).all()
    county = [(i.county_id, i.county_ch_name) for i in county]
    return county


def get_one_accommodation(accommodation_id):
    accommodation = (
        db_session.query(Accommodation)
        .filter(Accommodation.accommodation_id == accommodation_id)
        .first()
    )
    return accommodation


def get_accommodation_live():
    accommodation = db_session.query(
        Accommodation.accommodation_id,
        Accommodation.accommodation_ch_name,
        Accommodation.county_id,
    ).all()
    return accommodation


def update_accommodation(accommodation_id, form):
    db_session.query(Accommodation).filter(
        Accommodation.accommodation_id == accommodation_id
    ).update(
        {
            "accommodation_name": form.accommodation_name.data,
            "accommodation_ch_name": form.accommodation_ch_name.data,
            "address": form.address.data,
            "ch_address": form.ch_address.data,
            "phone_number": form.phone_number.data,
            "wifi": form.wifi.data,
            "county_id": form.county_id.data,
            "elevation": form.elevation.data,
            "note": form.note.data,
        }
    )
    db_session.commit()


def insert_accommodation(form):
    new_accommodation = Accommodation(
        accommodation_name=form.accommodation_name.data,
        accommodation_ch_name=form.accommodation_ch_name.data,
        address=form.address.data,
        ch_address=form.ch_address.data,
        phone_number=form.phone_number.data,
        wifi=form.wifi.data,
        county_id=form.county_id.data,
        elevation=form.elevation.data,
        note=form.note.data,
    )
    db_session.add(new_accommodation)
    db_session.commit()


def _insert_an_itinerary_alchemy(itinerary_id, itinerary_response: dict):
    # insert itinerary and itinerary_accommdation table
    schedules = []
    accommodations = []

    for i, s in enumerate(itinerary_response["schedule"]):
        for j, sp in enumerate(s["spots"]):

            new_schedule = Itinerary(
                itinerary_id=itinerary_id,
                day=i,
                schedule=j + 1,
                spot_id=int(sp),
            )
            schedules.append(new_schedule)

        new_accommodation = ItineraryAccommodation(
            itinerary_id=itinerary_id,
            day=i,
            accommodation_id=int(s["accommodation"]),
        )
        accommodations.append(new_accommodation)
    db_session.add_all(schedules)
    db_session.commit()
    db_session.add_all(accommodations)
    db_session.commit()


def insert_an_itinerary(itinerary_response: dict):

    # insert itinerary_title table
    new_itinerary_title = ItineraryTitle(
        title=itinerary_response["title"],
        ch_title=itinerary_response["ch_title"],
        invalid=0,
    )
    db_session.add(new_itinerary_title)
    db_session.commit()
    max_id = db_session.query(func.max(ItineraryTitle.itinerary_id)).first()[0]

    _insert_an_itinerary_alchemy(max_id, itinerary_response)


def update_an_itinerary(itinerary_id, itinerary_response: dict):
    db_session.query(ItineraryTitle).filter(
        ItineraryTitle.itinerary_id == itinerary_id
    ).update(
        {
            "title": itinerary_response["title"],
            "ch_title": itinerary_response["ch_title"],
        }
    )
    db_session.commit()

    db_session.query(Itinerary).filter(Itinerary.itinerary_id == itinerary_id).delete()
    db_session.commit()
    db_session.query(ItineraryAccommodation).filter(
        ItineraryAccommodation.itinerary_id == itinerary_id
    ).delete()
    db_session.commit()

    _insert_an_itinerary_alchemy(itinerary_id, itinerary_response)


def get_spot_title(spot_id):
    spot_title = (
        db_session.query(Spot.spot_name, Spot.spot_ch_name)
        .filter(Spot.spot_id == spot_id)
        .first()
    )
    return spot_title


def key_species_spot_or_not(spot_id):
    key_species = (
        db_session.query(SpeciesSpot.key_species_id)
        .filter(SpeciesSpot.spot_id == spot_id)
        .all()
    )
    key_species = [i[0] for i in key_species]

    statment = case([(KeySpecies.key_species_id.in_(key_species), 1)], else_=0).label(
        "is_spot_key"
    )

    is_key_species = db_session.query(KeySpecies, statment).all()

    return is_key_species


def update_spot_key_spcies(spot_id: int, key_species: list):
    key_species = [int(i) for i in key_species]

    spot_species = (
        db_session.query(SpeciesSpot.key_species_id)
        .filter(SpeciesSpot.spot_id == spot_id)
        .all()
    )

    spot_species = [i[0] for i in spot_species]
    remove_species_id = list(set(spot_species) - set(key_species))
    add_species_id = list(set(key_species) - set(spot_species))

    db_session.query(SpeciesSpot).filter(
        and_(
            SpeciesSpot.spot_id == spot_id,
            SpeciesSpot.key_species_id.in_(remove_species_id),
        )
    ).delete()
    db_session.commit()

    add_speices = []
    for i in add_species_id:
        new_speices = SpeciesSpot(spot_id=spot_id, key_species_id=i)
        add_speices.append(new_speices)

    db_session.add_all(add_speices)
    db_session.commit()


def invalid_itinerary(itinerary_id):
    db_session.query(ItineraryTitle).filter(
        ItineraryTitle.itinerary_id == itinerary_id
    ).update(
        {
            "invalid": 1,
        }
    )
    db_session.commit()


def get_itinerary_selection():
    itineraries = (
        db_session.query(ItineraryTitle.itinerary_id, ItineraryTitle.ch_title)
        .filter(ItineraryTitle.invalid == 0)
        .all()
    )

    empty_choice = ("", "---")
    itineraries.insert(0, empty_choice)
    return itineraries


def get_one_user(user_id: int):
    user = db_session.query(User).filter(User.user_id == user_id).first()
    return user


def get_user_by_username(email: str):
    user = db_session.query(User).filter(User.user_name == email).first()
    return user


def get_users():
    users = db_session.query(User).all()
    user_dict = {}
    for i in users:
        user_dict[i.user_name] = {}
        user_dict[i.user_name]["password"] = i.password
    return user_dict


if __name__ == "__main__":
    query = get_one_itinerary_spot_quote(6)
    print(query)
