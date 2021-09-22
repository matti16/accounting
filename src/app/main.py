
import datetime
import sys
import os
import time

sys.path.append("../")

from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from accounting.checks import AccountChecks, VatChecks
from patch_file import PatchedSpooledTempfile

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


def delete_tmp_file(filepath: str):
    wait_sec = 15
    time.sleep(wait_sec)
    os.remove(filepath)



@app.post("/uploadfiles/accounts")
async def upload_files(background_tasks: BackgroundTasks, bank_file: UploadFile = File(...), registered_file: UploadFile = File(...)):
    bank_fmt = bank_file.filename.split(".")[-1]
    registered_fmt = registered_file.filename.split(".")[-1]
    checker = AccountChecks(
        PatchedSpooledTempfile(bank_file.file), 
        PatchedSpooledTempfile(registered_file.file), 
        bank_fmt=bank_fmt, 
        income_fmt=registered_fmt
    )
    diff = checker.get_differences()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    result_file = os.path.join("tmp", f"differenze_{timestamp}.xlsx")
    diff.to_excel(result_file, index=False)
    background_tasks.add_task(delete_tmp_file, result_file)
    return FileResponse(path=result_file, filename="differenze.xlsx")

@app.post("/uploadfiles/vat")
async def upload_files(background_tasks: BackgroundTasks, vat_file: UploadFile = File(...)):
    vat_fmt = vat_file.filename.split(".")[-1]
    checker = VatChecks(
        PatchedSpooledTempfile(vat_file.file), 
        vat_fmt
    )
    diff = checker.get_differences()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    result_file = os.path.join("tmp", f"differenze_{timestamp}.xlsx")
    diff.to_excel(result_file, index=False)
    background_tasks.add_task(delete_tmp_file, result_file)
    return FileResponse(path=result_file, filename="differenze.xlsx")
    