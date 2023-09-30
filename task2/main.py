import math
from datetime import date
from pathlib import Path

import pandas as pd
from sqlalchemy import Date, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Business(Base):
    __tablename__ = "business"

    bin: Mapped[str] = mapped_column(primary_key=True)
    full_name_ru: Mapped[str] = mapped_column(String(10000))
    data_registration: Mapped[date] = mapped_column(Date)
    oked: Mapped[str] = mapped_column(String(100))
    additional_oked: Mapped[str] = mapped_column(String(10000))
    krp: Mapped[str] = mapped_column(String(100))
    kato: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f"Business(bin={self.bin!r}, full_name_ru={self.full_name_ru!r})"


# Making connection
engine = create_engine("postgresql://myuser:mypassword@localhost:5432/postgres")

# Creating schema
Base.metadata.create_all(engine)

# Reading excel
excel_data_file = (
    Path(__file__).parent / "request-94043238e76b0f457aafb48aaecee937.xlsx"
)

df = pd.read_excel(excel_data_file, index_col=None, header=1, engine="openpyxl")

# Inserting data
all = []
for index, row in df.iterrows():
    if math.isnan(row["БИН"]):
        continue

    business = Business(
        bin=str(int(row["БИН"])),
        full_name_ru=row["Полное наименование "],
        data_registration=row["Дата регистрации"].date(),
        oked=str(row["ОКЭД"]),
        additional_oked=(
            ""
            if (type(row["Втор.ОКЭД"]) is not str) and math.isnan(row["Втор.ОКЭД"])
            else str(row["Втор.ОКЭД"])
        ),
        krp=str(row["КРП"]),
        kato=str(row["КАТО"]),
    )
    all.append(business)

with Session(engine) as session:
    session.add_all(all)
    session.commit()
