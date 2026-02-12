from fastapi import FastAPI , Path ,HTTPException , Query
import json

app=FastAPI()

def load_data():
    with open('patients.json','r') as f:
        data=json.load(f)
    return data

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
