from sqlalchemy import Column, Integer, String, Text
from database import Base

class User(Base):

    __tablename__ = "Hotel"
    
    id=Column(Integer,primary_key=True,index=True)

    Property_code = Column(String(100),nullable=False)

    Bearer = Column(String(100), nullable=False)

    Key = Column(String(100),nullable=False)

    Endpoint = Column(String(100),nullable=False)                                                    


class Hoteldata(Base):

    __tablename__ = "hoteldata"
    
    reservation_id=Column(String(100),primary_key=True)

    confirmation_no=Column(String(100))

    first_name=Column(String(100))

    last_name=Column(String(100))

    room_no=Column(String(100))


class Tokengen(Base):
   __tablename__="tokengen"

   id = Column(Integer, primary_key=True, index=True)

   token = Column(Text, nullable=False)
    