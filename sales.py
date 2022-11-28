from datetime import date
import json
from typing import Union
from fastapi import FastAPI, Response, status, Header, Request
from dotenv import load_dotenv
from pydantic import BaseModel
from utils import get_hash, encode_token, SECRET, authorize
import jwt
load_dotenv()

with open("penjualan.json", "r") as read_file:
    data = json.load(read_file)
    
with open("user.json", "r") as read_file:
    akun = json.load(read_file)

app = FastAPI()

class LoginParamater(BaseModel):
    username: str
    password: str

@app.post('/login')
def login(param: LoginParamater, response: Response):
    found = False
    # print(param.username)
    # print(param.password)
    for i in range (len(akun)) :
        if (param.username == akun[i]["username"]):
            found = True
            if (get_hash(param.password) == akun[i]["password"]):
                token = encode_token(param.username)
                print(token)
                return { 
                    "message": "Login Sukses",
                    "data": { "token": token }
                }
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return { "message": "Password Salah Say"}
    if not found:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "User not found!" }
    
# @app.get('/')
# def identitas():
#     return {'Andreana Hartadi Suliman (18220027)'}

#Read Data Warehouse
@app.get('/penjualan')
async def get_sales(request: Request):
    authorize(request)
    return data["penjualan"]

class AddNota(BaseModel):
    nama: str
    kuantitas: float
    hargaPerLusin: float
    
#Add New Data
@app.post('/penjualan')
async def add_nota(request: Request, param: AddNota):
    authorize(request)
    idNota = 1
    today = date.today()
    if (len(data["penjualan"]) > 0) :
        idNota = data["penjualan"][len(data["penjualan"]) - 1]["idNota"] + 1
    new_data = {
        'idNota': idNota, 
        'tanggal': today.strftime("%Y-%m-%d"), 
        'nama': param.nama, 
        'kuantitas': param.kuantitas, 
        'hargaPerLusin': param.hargaPerLusin, 
        'totalHarga': param.kuantitas*param.hargaPerLusin}
    data["penjualan"].append(dict(new_data))

    with open("penjualan.json", "w") as write_file :
        json.dump(data, write_file, indent = 4)
    return {"message": "Data nota berhasil ditambahkan"}
    write_file_close()