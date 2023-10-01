import math
from datetime import date, datetime
from pathlib import Path
from typing import Optional
from pymongo import MongoClient

import pandas as pd
from sqlalchemy import Date, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class BusinessWrongAddress(Base):
    __tablename__ = "business_wrong_address"

    bin: Mapped[str] = mapped_column(primary_key=True)
    rhh: Mapped[str] = mapped_column(String(20))
    full_name: Mapped[str] = mapped_column(String(500))
    tax_payers_full_name: Mapped[str] = mapped_column(String(50))
    directors_full_name: Mapped[str] = mapped_column(String(50))
    directors_iin: Mapped[str] = mapped_column(String(20))
    directors_rhh: Mapped[str] = mapped_column(String(20))
    investigation_number: Mapped[str] = mapped_column(String(150))
    investigation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:
        return f"Business(bin={self.bin!r}, full_name={self.full_name!r})"


class BusinessBankrupt(Base):
    __tablename__ = "business_bankrupt"

    bin: Mapped[str] = mapped_column(primary_key=True)
    rhh: Mapped[str] = mapped_column(String(20))
    full_name: Mapped[str] = mapped_column(String(500))
    tax_payers_full_name: Mapped[str] = mapped_column(String(50))
    directors_full_name: Mapped[str] = mapped_column(String(50))
    directors_iin: Mapped[str] = mapped_column(String(20))
    directors_rhh: Mapped[str] = mapped_column(String(20))
    court_number_txt: Mapped[str] = mapped_column(String(10000))
    court_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:
        return f"Business(bin={self.bin!r}, full_name={self.full_name!r})"


class BusinessInvalidRegistration(Base):
    __tablename__ = "business_invalid_registration"

    bin: Mapped[str] = mapped_column(primary_key=True)
    rhh: Mapped[str] = mapped_column(String(500))
    full_name: Mapped[str] = mapped_column(String(10000))
    tax_payers_full_name: Mapped[str] = mapped_column(String(10000))
    directors_full_name: Mapped[str] = mapped_column(String(10000))
    directors_iin: Mapped[str] = mapped_column(String(500))
    directors_rhh: Mapped[str] = mapped_column(String(500))
    court_number_txt: Mapped[str] = mapped_column(String(10000))
    court_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:
        return f"Business(bin={self.bin!r}, full_name={self.full_name!r})"


def check_if_nan(x):
    if type(x) is float and math.isnan(x):
        return True
    if x == "":
        return True
    return False


def convert_to_date(x):
    if check_if_nan(x):
        return None
    if type(x) is str:
        return datetime.strptime(x, "%Y-%m-%d %H:%M:%S").date()
    raise ValueError


def read_wrong_address(mongodb, postgre_engine):
    # The list of taxpayers, absent the legal address
    file_path = Path(__file__).parent / "list_WRONG_ADDRESS_KZ_ALL.xlsx"
    df = pd.read_excel(
        file_path,
        index_col=None,
        header=2,
        engine="openpyxl",
        converters={
            "ЖСН/БСН\nИИН/БИН": str,
            "СТН\nРНН": str,
            "Басшысының ЖСН \nИИН руководителя": str,
            "Басшысының СТН\nРНН руководителя": str,
            "Тексеру актінің нөмірі\nНомер акта обследования": str,
            "Тексеру актінің күні\nДата акта обследования": str,
        },
    )
    df = df.fillna("")

    # Inserting data
    all = []
    for index, row in df.iterrows():
        if check_if_nan(row["ЖСН/БСН\nИИН/БИН"]):
            continue

        business = BusinessWrongAddress(
            bin=row["ЖСН/БСН\nИИН/БИН"],
            rhh=row["СТН\nРНН"],
            full_name=row["Салық төлеушінің атауы\nНаименование  налогоплательщика"],
            tax_payers_full_name=row[
                "Салық төлеушінің аты-жөні\nФИО налогоплательщика"
            ],
            directors_full_name=row["Басшысының аты-жөні\nФИО руководителя"],
            directors_iin=row["Басшысының ЖСН \nИИН руководителя"],
            directors_rhh=row["Басшысының СТН\nРНН руководителя"],
            investigation_number=row["Тексеру актінің нөмірі\nНомер акта обследования"],
            investigation_date=convert_to_date(
                row["Тексеру актінің күні\nДата акта обследования"]
            ),
        )
        all.append(business)

    # mongo
    collection_name = mongodb[BusinessWrongAddress.__tablename__]
    all_dict = []
    for obj in all:
        ddict = {}
        for x, y in obj.__dict__.items():
            if x.startswith("_"):
                continue
            if type(y) is date:
                y = datetime.combine(y, datetime.min.time())
            ddict[x] = y
        all_dict.append(ddict)
    collection_name.insert_many(all_dict)

    # postgre
    with Session(postgre_engine) as session:
        session.add_all(all)
        session.commit()


def read_bankrupt(mongodb, postgre_engine):
    # The list of taxpayers declared bankrupt
    file_path = Path(__file__).parent / "list_BANKRUPT_KZ_ALL.xlsx"
    df = pd.read_excel(
        file_path,
        index_col=None,
        header=2,
        engine="openpyxl",
        converters={
            "ЖСН/БСН\nИИН/БИН": str,
            "СТН\nРНН": str,
            "Басшысының ЖСН \nИИН руководителя": str,
            "Басшысының СТН\nРНН руководителя": str,
            "Сот шешімінің күні\nДата решения суда": str,
        },
    )
    df = df.fillna("")

    # Inserting data
    all = []
    for index, row in df.iterrows():
        if check_if_nan(row["ЖСН/БСН\nИИН/БИН"]):
            continue

        business = BusinessBankrupt(
            bin=row["ЖСН/БСН\nИИН/БИН"],
            rhh=row["СТН\nРНН"],
            full_name=row["Салық төлеушінің атауы\nНаименование  налогоплательщика"],
            tax_payers_full_name=row[
                "Салық төлеушінің аты-жөні\nФИО налогоплательщика"
            ],
            directors_full_name=row["Басшысының аты-жөні\nФИО руководителя"],
            directors_iin=row["Басшысының ЖСН \nИИН руководителя"],
            directors_rhh=row["Басшысының СТН\nРНН руководителя"],
            court_number_txt=row["Сот шешімінің нөмірі\nНомер решения суда"],
            court_date=convert_to_date(row["Сот шешімінің күні\nДата решения суда"]),
        )
        all.append(business)

    # mongo
    collection_name = mongodb[BusinessBankrupt.__tablename__]
    all_dict = []
    for obj in all:
        ddict = {}
        for x, y in obj.__dict__.items():
            if x.startswith("_"):
                continue
            if type(y) is date:
                y = datetime.combine(y, datetime.min.time())
            ddict[x] = y
        all_dict.append(ddict)
    collection_name.insert_many(all_dict)

    # postgre
    with Session(postgre_engine) as session:
        session.add_all(all)
        session.commit()


def read_invalid_registration(mongodb, postgre_engine):
    # The list of taxpayers whose registration is declared invalid
    file_path = Path(__file__).parent / "list_INVALID_REGISTRATION_KZ_ALL.xlsx"
    df = pd.read_excel(
        file_path,
        index_col=None,
        header=2,
        engine="openpyxl",
        converters={
            "ЖСН/БСН\nИИН/БИН": str,
            "СТН\nРНН": str,
            "Басшысының ЖСН \nИИН руководителя": str,
            "Басшысының СТН\nРНН руководителя": str,
            "Сот шешімінің күні\nДата решения суда": str,
        },
    )
    df = df.fillna("")

    # Inserting data
    all = []
    for index, row in df.iterrows():
        if check_if_nan(row["ЖСН/БСН\nИИН/БИН"]):
            continue

        business = BusinessInvalidRegistration(
            bin=row["ЖСН/БСН\nИИН/БИН"],
            rhh=row["СТН\nРНН"],
            full_name=row["Салық төлеушінің атауы\nНаименование  налогоплательщика"],
            tax_payers_full_name=row[
                "Салық төлеушінің аты-жөні\nФИО налогоплательщика"
            ],
            directors_full_name=row["Басшысының аты-жөні\nФИО руководителя"],
            directors_iin=row["Басшысының ЖСН \nИИН руководителя"],
            directors_rhh=row["Басшысының СТН\nРНН руководителя"],
            court_number_txt=row["Сот шешімінің нөмірі\nНомер решения суда"],
            court_date=convert_to_date(row["Сот шешімінің күні\nДата решения суда"]),
        )
        all.append(business)

    # mongo
    collection_name = mongodb[BusinessInvalidRegistration.__tablename__]
    all_dict = []
    for obj in all:
        ddict = {}
        for x, y in obj.__dict__.items():
            if x.startswith("_"):
                continue
            if type(y) is date:
                y = datetime.combine(y, datetime.min.time())
            ddict[x] = y
        all_dict.append(ddict)
    collection_name.insert_many(all_dict)

    # postgre
    with Session(postgre_engine) as session:
        session.add_all(all)
        session.commit()


def get_mongo_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://madibekovnurbakhyt:helloworld@cluster0.omum77e.mongodb.net/?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client["business_lists"]


if __name__ == "__main__":
    ## MongoDB
    mongodb = get_mongo_database()

    ## PostgreSQL
    # Making connection
    postgre_engine = create_engine(
        "postgresql://myuser:mypassword@localhost:5432/postgres"
    )

    # Creating schema
    Base.metadata.create_all(postgre_engine)

    print("Populating wrong address data")
    read_wrong_address(mongodb, postgre_engine)

    print("Populating bankrupt data")
    read_bankrupt(mongodb, postgre_engine)

    print("Populating invalid registration data")
    read_invalid_registration(mongodb, postgre_engine)
