from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()


class ElevatorStatus(str, Enum):
    FREE = "Free"
    BUSY = "Busy"
    OUT_OF_SERVICE = "Out of Service"


class Elevator(BaseModel):
    Floor: int = Field(..., ge=0, le=10)
    CFloors: int = Field(0, ge=0, le=10)
    DFloor: Optional[int] = Field(0, description="Destination floor", ge=0, le=10)
    status: ElevatorStatus = ElevatorStatus.FREE

    def move_elevator(self):
        if self.status != ElevatorStatus.FREE:
            raise HTTPException(status_code=400, detail="Elevator is in Use")
        elif self.status == ElevatorStatus.OUT_OF_SERVICE:
            raise HTTPException(status_code=400, detail="Elevator is Out of Service")
        if self.CFloors > self.DFloor:
            self.status = ElevatorStatus.BUSY
            self.CFloors = self.DFloor
            return {"ResponseMessage": "Elevator is going Down", "ResponseCode": "00"}
        elif self.CFloors < self.DFloor:
            self.status = ElevatorStatus.BUSY
            self.CFloors = self.DFloor
            return {"ResponseMessage": "Elevator is going up", "ResponseCode": "00"}
        else:
            return {"ResponseMessage": "Elevator is already at the requested floor", "ResponseCode": "00"}

    def update_status(self):
        if self.status == ElevatorStatus.BUSY:
            self.status = ElevatorStatus.FREE
            return {"ResponseMessage": "Elevator status is updated", "ResponseCode": "00"}


class User:
    def __init__(self, elevator: Elevator):
        self.elevator = elevator

    def call_elevator(self):
        if self.elevator.status != ElevatorStatus.FREE:
            raise HTTPException(status_code=400, detail="Elevator is in Use")
        elif self.elevator.status == ElevatorStatus.OUT_OF_SERVICE:
            raise HTTPException(status_code=400, detail="Elevator is Out of Service")

        if self.elevator.status == ElevatorStatus.FREE:
            self.elevator.CFloors = self.elevator.DFloor
            self.elevator.status = ElevatorStatus.BUSY
            return {"ResponseMessage": f"Elevator is going to {self.elevator.DFloor}", "ResponseCode": "00"}
        else:
            raise HTTPException(status_code=400, detail="You cannot call the elevator on the current floor")


# Create an instance of Elevator
elevator_instance = Elevator(Floor=0, CFloors=0, DFloor=None)


@app.post("/move_elevator")
async def move_elevator(target_floor: int):
    # Use the existing instance and update the DFloor
    elevator_instance.DFloor = target_floor
    return elevator_instance.move_elevator()


@app.post("/call_elevator")
async def call_elevator(destination_floor: int):
    # Create an instance of User and call the call_elevator method
    user_instance = User(elevator_instance)
    return user_instance.call_elevator()


@app.get("/elevator_status")
async def get_elevator_status():
    return {"status": elevator_instance.status.value}


@app.get("/status_update")
async def update_status_update():
    # Call the update_status method to update the elevator status
    return elevator_instance.update_status()


@app.get("/get_currentFloor")
async def get_current_floor():
    # Call the update_status method to update the elevator status
    return {"CurrentFloor": elevator_instance.CFloors}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8211)
