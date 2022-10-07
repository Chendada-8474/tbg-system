from sqlalchemy import create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import func
from datetime import date, datetime


engine = create_engine(
    "mysql+pymysql://root:ro2231031@192.168.1.104:3306/taiwanbirdguide"
)
Base = declarative_base()
Base.metadata.reflect(engine)
db_session = scoped_session(sessionmaker(bind=engine))

STATUS_COL = ["to_quote", "deposit", "pay_off", "trip_end", "accounted"]
TRIP_STATUS = ["quote sent", "got deposit", "paid off", "trip finished", "reimbursed"]


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
        db_session.query(Trip, Customer, Car, Country, BankAccount)
        .join(Customer, Trip.contact_client == Customer.customer_id)
        .join(Car, Trip.vehicle == Car.car_id)
        .join(BankAccount, Trip.receiving_account == BankAccount.bank_account_id)
        .join(Country, Customer.country == Country.country_id)
        .filter(Trip.trip_id == id)
        .all()
    )
    return trip_info


def get_one_trip(id):
    trip_info = db_session.query(Trip).filter(Trip.trip_id == id).first()

    return trip_info


def get_trip_partner(id):
    guide = (
        db_session.query(Trip.trip_id, Partner.first_name, Partner.last_name)
        .join(Partner, Trip.guide == Partner.partner_id)
        .filter(Trip.trip_id == id)
        .all()
    )
    driver = (
        db_session.query(Trip.trip_id, Partner.first_name, Partner.last_name)
        .join(Partner, Trip.driver == Partner.partner_id)
        .filter(Trip.trip_id == id)
        .all()
    )
    manager = (
        db_session.query(Trip.trip_id, Partner.first_name, Partner.last_name)
        .join(Partner, Trip.manager == Partner.partner_id)
        .filter(Trip.trip_id == id)
        .all()
    )
    sales = (
        db_session.query(Trip.trip_id, Partner.first_name, Partner.last_name)
        .join(Partner, Trip.sales == Partner.partner_id)
        .filter(Trip.trip_id == id)
        .all()
    )
    accountant = (
        db_session.query(Trip.trip_id, Partner.first_name, Partner.last_name)
        .join(Partner, Trip.accountant == Partner.partner_id)
        .filter(Trip.trip_id == id)
        .all()
    )
    route_control = (
        db_session.query(Trip.trip_id, Partner.first_name, Partner.last_name)
        .join(Partner, Trip.route_control == Partner.partner_id)
        .filter(Trip.trip_id == id)
        .all()
    )

    crew = {
        "guide": "%s %s" % (guide[0][1], guide[0][2]),
        "driver": "%s %s" % (driver[0][1], driver[0][2]),
        "manager": "%s %s" % (manager[0][1], manager[0][2]),
        "sales": "%s %s" % (sales[0][1], sales[0][2]),
        "accountant": "%s %s" % (accountant[0][1], accountant[0][2]),
        "route_control": "%s %s" % (route_control[0][1], route_control[0][2]),
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


def update_progress(id: int, progress: list, how=None):
    if not how:
        return
    elif how == "next":
        for i, p in enumerate(progress):
            if p == 0:
                upd = (
                    db_session.query(Trip)
                    .filter(Trip.trip_id == id)
                    .update({STATUS_COL[i]: 1})
                )
                break
    elif how == "back":
        cols = list(reversed(STATUS_COL))
        progress.reverse()
        for i, p in enumerate(progress):
            if p == 1:
                upd = (
                    db_session.query(Trip)
                    .filter(Trip.trip_id == id)
                    .update({cols[i]: 0})
                )
                break
    elif how == "cancel":
        upd = db_session.query(Trip).filter(Trip.trip_id == id).update({"cancel": 1})
    elif how == "uncancel":
        upd = db_session.query(Trip).filter(Trip.trip_id == id).update({"cancel": 0})
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
    max_id = db_session.query(func.max(Customer.customer_id)).all()[0][0]
    return max_id


def get_max_trip_id():
    max_id = db_session.query(func.max(Trip.trip_id)).all()[0][0]
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
        currency=form.currency.data,
        pick_up_time=form.pick_up_time.data,
        pick_up_location=form.pick_up_location.data,
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


def update_trip(id, form):
    db_session.query(Trip).filter(Trip.trip_id == id).update(
        {
            "starting_date": form.starting_date.data,
            "number_of_days": form.number_of_days.data,
            "cost": form.cost.data,
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


def expenditure_summary(exp_info, trip_info):
    total_expend = 0

    try:
        for i in exp_info:
            total_expend += i[0].unit_price * i[0].quantity
        profit = trip_info[0][0].cost * trip_info[0][0].exchange_rate - total_expend
    except:
        total_expend = None
        profit = None

    return total_expend, profit


if __name__ == "__main__":

    print()
