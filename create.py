from fastapi import FastAPI , Path ,HTTPException , Query
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel, computed_field , Field
from typing import Annotated, Literal

app=FastAPI()

class Patient(BaseModel):
    id:Annotated[str,Field(...,description ="id of patient",example=["P001"])]
    name : Annotated[str,Field(...,description="name of patient")]
    city:Annotated[str,Field(...,description="city of patient")]
    age:Annotated[int,Field(...,gt=0,lt=120,description="age of patient")]
    gender:Annotated[Literal["Male","Female","Other"],Field(...,description="gender of patient")]
    height:Annotated[float,Field(...,gt=0,description="height of patient")]
    weight:Annotated[float,Field(...,gt=0,description="weight of patient")]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi=round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi<18.5:
            return "Underweight"
        elif self.bmi>=18.5 and self.bmi<25:
            return "Normal weight"
        elif self.bmi>=25 and self.bmi<30:
            return "Overweight"
        else:
            return "Obese"






def load_data():
    with open('patients.json','r') as f:
        data=json.load(f)
    return data

def save_data(data):
    with open("patient.json","w") as f:
        json.dump(data,f)

@app.get("/")
def hello():
    return {"Patient managemnet system "}
 
@app.get("/about")
def about():
    return{"message:A full functional Api to manage "}
    
@app.get("/view")
def view():
    data=load_data()
    return data

#path parameter : specific data dekhna ho to

@app.get('/patient/{patient_id}')    #path parameters:specific ek patient ka data dekhna hai to uska url create kar rahe hai 
def view_patient(patient_id : str = Path(..., description='ID of the patient in the DB ', example='P001')):  #path detailing ke liye 
    data=load_data()
    if patient_id in data:
        return data[patient_id]

    raise HTTPException(status_code=404 , detail="Patient not found")  #if patient id not found 

#query selector : sorting filtering searching pagination ..
#each parameter is a key value parameter 


@app.get('/sort')
def sortpatient(sort_by : str = Query(..., description="sort on the basis of "),
                order : str =Query("asc", description="sort in ascending or decneding")):

    valid_fields=["height","weight","bmi"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=404 , detail=f"invalid field select from {valid_fields}")
    
    if order not in ["asc","desc"]:
        raise HTTPException(status_code=404 , detail="invalid")
    
    data=load_data()
    sort_order= True if order=="desc" else False
    sort_data=sorted(data.values() , key=lambda x: x.get(sort_by ,0),reverse=sort_order)
    return sort_data

#createing a new patient
@app.post("/create")
def create_patient(patient: Patient):
    #load existing data
    data=load_data()

    #check id patient already exist 
    if patient.id in data :
        raise HTTPException(status_code=400 , detail="patient exists")

    #if new patient then add
    data[patient.id]=patient.model_dump(exclude=["id"])
    # save in jason file

    save_data(data)

    return JSONResponse(status_code=201, content={"message": "Patient created successfully", "patient": patient.model_dump(exclude=["id"])})






