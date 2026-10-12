from fastapi import FastAPI, Depends, HTTPException,Body
from sqlalchemy.orm import Session
from models import User,Hoteldata,Tokengen
from database import engine, Base, get_db
from schemas import UserCreate,HoteltableCreate,TokenCreate
from database import sync_database
import httpx
import jwt,json,requests
from datetime import datetime, timedelta, timezone


app = FastAPI()
sync_database()

@app.post("/users")
def create_user(user_data: UserCreate,db: Session = Depends(get_db)):
    user = User(
        Property_code=user_data.Property_code,
        Bearer=user_data.Bearer,
        Key=user_data.Key,
        Endpoint=user_data.Endpoint,
             )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

import requests
@app.get("/data/{property}")
async def get_users(property: str,db: Session = Depends(get_db)):
    user_details=db.query(User).filter(User.Property_code == property).first()
    key    = user_details.Key
    bearer = user_details.Bearer
    endpoint = user_details.Endpoint
    url=f"{endpoint}/api/PassportScanner/guest-arrivals"
    headers={
        "Authorization":bearer ,
        "x-api-key": key 
            }
    async with httpx.AsyncClient() as client:
        response = httpx.AsyncClient().get(
                url,
                headers=headers
            )
    return response.json()
    # response = requests.get(url=url,headers=headers)
    # return response.json()

@app.get("/apidata/{property}")
def apidata(property: str,db: Session=Depends(get_db)):
    api_data=get_users(property,db)
    arrival_data=api_data.get("Arrivals")
    l=[]
    for i in arrival_data:
        l.append({
            "reservation_id" :i.get("ReservationId"),
            "confirmation_no":i.get("ConfirmationNumber"),
            "first_name":i.get("GuestDetails",{}).get("FirstName"),
            "last_name":i.get("GuestDetails",{}).get("LastName"),
            "room_no":i.get("RoomDetails",{}).get("RoomNumber")
        })
    #    reservation_id=i.get("ReservationId")
    #    return reservation_id
    # reservation_id=arrival_data.get("ReservationId")
    return l


@app.post("/hoteldata/{property}")
async def create_hotel(property: str,db: Session = Depends(get_db)):
    listdata=await apidata(property,db)
    for i in listdata:
       hotel_data = Hoteldata(
        reservation_id=i.get("reservation_id"),
        confirmation_no=i.get("confirmation_no"),
        first_name=i.get("first_name"),
        last_name=i.get("last_name"),
        room_no=i.get("last_name"))
       db.add(hotel_data)
       db.commit()
       db.refresh(hotel_data)
    return hotel_data
    

@app.get("/getsinglerow")
def getsingledata(name:dict=Body(...),db: Session = Depends(get_db)):
    if name.get("confirmation_no"):
        confirmationno=name.get("confirmation_no")
        hotel_details=db.query(Hoteldata).filter(Hoteldata.reservation_id == confirmationno).first()
        if hotel_details:
            return hotel_details
    elif name.get("reservation_id"):
        reservationid=name.get("reservation_id")
        hotel_details=db.query(Hoteldata).filter(Hoteldata.last_name == reservationid).first()
        if hotel_details:
           return hotel_details
    elif name.get("first_name"):
        firstname=name.get("first_name")   
        hotel_details=db.query(Hoteldata).filter(Hoteldata.first_name == firstname).first()
        if hotel_details:
          return hotel_details
    elif name.get("last_name"):
        lastname=name.get("last_name")
        hotel_details=db.query(Hoteldata).filter(Hoteldata.room_no == lastname).first()
        if hotel_details:
         return hotel_details
    elif name.get("room_no"):
        roomno=name.get("room_no")
        hotel_details=db.query(Hoteldata).filter(Hoteldata.confirmation_no == roomno).first()
        if hotel_details:
          return hotel_details
    

@app.get("/token")
def tokengenaration(db: Session = Depends(get_db)):
    secret_key="hemanth"
    ALGORITHM = "HS256"
    data=json.dumps(datetime.now(timezone.utc) + timedelta(hours=1),default=str)
    payload={
        "expiry":data 

    }
    bearer_token = jwt.encode(payload, secret_key, algorithm=ALGORITHM)
    token = Tokengen(
        token=bearer_token)

    db.add(token)
    db.commit()
    db.refresh(token)
    valid_token=db.query(Tokengen).filter(Tokengen.token == bearer_token).first()
    if valid_token:
        return valid_token
    else:
        return "invalid token"
    

@app.get("/tokenvalid")
def tokenvalidation(name:dict=Body(...),db: Session = Depends(get_db)):
    validtoken=name.get("validtoken")
    valid_token=db.query(Tokengen).filter(Tokengen.token == validtoken).first()
    if valid_token:
        return "success"
    else:
        return "invalid token"
    
