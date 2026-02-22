from fastapi import FastAPI , Path ,HTTPException , Query
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel, computed_field , Field
from typing import Annotated, Literal, Optional

app=FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="id of patient", example="P001")]
    name: Annotated[str, Field(..., description="name of patient")]
    city: Annotated[str, Field(..., description="city of patient")]
    age: Annotated[int, Field(..., gt=0, lt=120)]
    gender: Annotated[Literal["Male","Female","Other"], Field(...)]
    height: Annotated[float, Field(..., gt=0)]
    weight: Annotated[float, Field(..., gt=0)]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / ((self.height / 100) ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal weight"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None , gt=0)]
    gender: Annotated[Optional[Literal["Male","Female","Other"]], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None,gt=0)]
    weight: Annotated[Optional[float], Field(default=None ,gt=0)]



def load_data():
    with open('patients.json','r') as f:
        data=json.load(f)
    return data

def save_data(data):
    with open("patients.json","w") as f:
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

@app.put("/edit/{patient_id}")
def update_patient(patient_id:str,patient_upadte :PatientUpdate):
    data=load_data()
     
    #patient id valid chcek
    if patient_id not in data:
        raise HTTPException(status_code=404 , details="Patient not found")
    
    #id patient id is valid then exracting information of that patient 

    existing_patient_info=data[patient_id]

    # we want patient update ke values and put it in existing_patient_info dict
    #for that we need to convert pyrantic model in dictionary 

    updated_patient_info=patient_upadte.model_dump(exclude_unset=True); #taaki saari value na aye 
    
    for key , value in updated_patient_info.items():    #extracting key and value in upadte dict
        existing_patient_info[key]=value; 
    

    #existing_patient_info -> pydantic object -> updated bmi + update verdict 
    existing_patient_info["id"]=patient_id
    patient_pydantic_object=Patient(**existing_patient_info) #computed field recalculated

    
    # ->pydantic object ->dict 

    existing_patient_info=patient_pydantic_object.model_dump(exclude="id");
    
    #new pydantic model then new computed fileds
    #saving it in data but if wight is changing computed also need to be changed
    data[patient_id]=existing_patient_info

    save_data(data)

    return JSONResponse(status_code=200 , content="patient updated")


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id :str):
    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404 , detail="patient not in data")
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200 ,content={"message:patient deleted"})


    






