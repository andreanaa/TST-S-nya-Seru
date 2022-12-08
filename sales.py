from datetime import date
import json
from typing import Union
from fastapi import FastAPI, Response, status, Header, Request, HTTPException
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
        'totalHarga': param.kuantitas*param.hargaPerLusin
    }
    data["penjualan"].append(dict(new_data))

    with open("penjualan.json", "w") as write_file :
        json.dump(data, write_file, indent = 4)
    return {"message": "Data nota berhasil ditambahkan"}

class LihatPenjualanBulanan(BaseModel):
    bulan: str
    
#Melihat Data Penjualan Bulan Tertentu
@app.get('/penjualan/dataPenjualanBulanan')
async def lihat_data_penjualan_bulanan(request: Request, param: LihatPenjualanBulanan):
    authorize(request)
    listNota = []
    found = False
    penjualan = 0
    for sales in data['penjualan']:
        tanggal = sales["tanggal"]
        month = tanggal[5:7]
        if (month == param.bulan):
            found = True
            listNota.append(sales)
            penjualan += sales["totalHarga"]
    if not found:
        return { "message": "Tidak Ada Penjualan di Bulan Masukan" }
    return listNota

#Melihat Data Total Penjualan Bulan Tertentu
@app.get('/penjualan/dataTotalPenjualanBulanan')
async def lihat_data_total_penjualan_bulanan(request: Request, param: LihatPenjualanBulanan):
    authorize(request)
    found = False
    penjualan = 0
    for sales in data['penjualan']:
        tanggal = sales["tanggal"]
        month = tanggal[5:7]
        if (month == param.bulan):
            found = True
            penjualan += sales["totalHarga"]
    if not found:
        return { "message": "Tidak Ada Penjualan di Bulan Masukan" }
    return penjualan

class UpdateNota(BaseModel):
    idNota: int
    nama: str
    kuantitas: float
    hargaPerLusin: float

#Update Data Nota
@app.put('/penjualan/nota')
async def update_nota(request: Request, param: UpdateNota):
    authorize(request)
    found = False
    for sales in data['penjualan']:
        if (param.idNota == sales["idNota"]):
            found = True
            sales["nama"] = param.nama
            sales["kuantitas"] = param.kuantitas
            sales["hargaPerLusin"] = param.hargaPerLusin
            sales["totalHarga"] = param.kuantitas * param.hargaPerLusin
            with open("penjualan.json", "w") as write_file :
                json.dump(data, write_file, indent = 4)
            return { "message": "Data barang berhasil diupdate" }
    if not found:
        return { "message": "ID Nota Tidak Ada" }

class DeleteNota(BaseModel):
    idNota: int

#Menghapus Data Nota
@app.delete('/penjualan/deleteNota')
async def delete_nota(request: Request, param: DeleteNota):
    authorize(request)
    found = False
    for sales in data['penjualan']:
        if (param.idNota == sales["idNota"]):
            found = True
            data['penjualan'].remove(sales)
            with open("penjualan.json", "w") as write_file :
                json.dump(data, write_file, indent = 4)
            return { "message": "Data Nota Berhasil Dihapus" }
    if not found:
        return { "message": "ID Nota Tidak Ada" }
  
class LiatPenjualanBarang(BaseModel):
    nama: str
    
#Melihat Data Penjualan Suatu Barang
@app.get('/penjualan/lihatDataPenjualanBarang')
async def lihat_data_penjualan_barang(request: Request, param: LiatPenjualanBarang):
    authorize(request)
    found = False
    penjualan = 0
    count = 0
    for sales in data['penjualan']:
        if (param.nama == sales["nama"]):
            found = True
            penjualan += sales["totalHarga"]
            count += sales["kuantitas"]
    if not found:
        return { "message": "Tidak Ada Data Penjualan Barang Masukan" }
    return {
        "message": [
            param.nama,
            "Total Penjualan",
            penjualan,
            "Total Barang Terjual",
            count
        ]
    }

class LiatLaba(BaseModel):
    nama: str
    bulan: str
    stok: float
    unitBeli: float
    hargaModal: float
    
#Menghitung Laba Kotor Suatu Barang
@app.get('/penjualan/hitungLaba')
async def lihat_laba(request: Request, param: LiatLaba):
    authorize(request)
    count = 0
    hargaJual = 0
    for sales in data['penjualan']:
        tanggal = sales["tanggal"]
        month = tanggal[5:7]
        if (param.nama == sales["nama"] and month == param.bulan):
            count += sales["kuantitas"]
            hargaJual = sales["hargaPerLusin"]
    if (count == 0):
        return { "message": "Tidak Ada Data Penjualan Barang Masukan" }
    labaKotor = count * hargaJual - param.hargaModal * (param.stok + param.unitBeli)
    if (labaKotor >= 0.5 * param.hargaModal):
        return {
            "message": [
                "Laba Kotor yang Didapat Adalah",
                labaKotor,
                "Kemungkinan Bulan Depan Perusahaan Akan Profit"
            ]
        }
    elif (labaKotor < 0.5 * param.hargaModal and labaKotor >= 0):
        return { 
            "message": [
                "Laba Kotor yang Didapat Adalah", 
                labaKotor
            ]
        }
    else:
        return {
            "message": [
                "Mengalami Kerugian Sebesar",
                labaKotor
            ]
        }