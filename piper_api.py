from fastapi import FastAPI
from pydantic import BaseModel
import piper_sdk
import piper_utils as pu
from data_utils import create_end_pose

app = FastAPI()
CAN_PORT = "can0"
MOVE_SPEED = 50  # 0 - 100

class MoveRobot(BaseModel):
    x: float
    y: float
    z: float
    rx: float
    ry: float
    rz: float
    gripper_angle: int  # in 0.001 degrees

def move_robot_helper(piper, move: MoveRobot, wait: bool = True):
    # Dealing with arm motion
    pose = [move.x, move.y, move.z, move.rx, move.ry, move.rz]
    x, y, z, rx, ry, rz = create_end_pose(pose)

    # Move to the target pose
    piper.EndPoseCtrl(x, y, z, rx, ry, rz)

    if wait:
        # Wait for the arm to finish moving
        pu.wait_end_of_movement(piper)

    # Gripper control
    gripper_angle = move.gripper_angle
    factor = 1000
    if gripper_angle >= 90000:
        piper.GripperCtrl(100 * factor, 1000, 0x01, 0)
    else:
        piper.GripperCtrl(0, 250, 0x01, 0)

    if wait:
        # Wait for the gripper action to complete
        pu.wait_end_of_movement(piper)


@app.post("/move")
async def move_robot(move: MoveRobot):
    # Initialize piper SDK
    piper = piper_sdk.C_PiperInterface_V2(CAN_PORT)
    piper.ConnectPort()

    try:
        piper.EnableArm(pu.USE_ALL_MOTOR)
        pu.enable_fun(piper=piper)
        piper.MotionCtrl_2(pu.CAN_CTRL_MODE,
                           pu.MOVE_POSITION_MODE,
                           MOVE_SPEED,
                           pu.POS_VELOCITY_MODE)

        # Move the robot to the target pose and handle the gripper
        move_robot_helper(piper, move)

        return {"status": "success", "message": "Robot moved successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        piper.DisconnectPort()
        return {"status": "disconnected", "message": "Port disconnected successfully!"}

@app.post("/move2")
async def move_robot_2(moves: list[MoveRobot]):
    # Initialize piper SDK
    piper = piper_sdk.C_PiperInterface_V2(CAN_PORT)
    piper.ConnectPort()

    try:
        piper.EnableArm(pu.USE_ALL_MOTOR)
        pu.enable_fun(piper=piper)
        piper.MotionCtrl_2(pu.CAN_CTRL_MODE,
                           pu.MOVE_POSITION_MODE,
                           MOVE_SPEED,
                           pu.POS_VELOCITY_MODE)

        # Execute each move sequentially
        for move in moves:
            move_robot_helper(piper, move)

        return {"status": "success", "message": "Robot moved successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        piper.DisconnectPort()
        return {"status": "disconnected", "message": "Port disconnected successfully!"}

@app.post("/move3")
async def move_robot_3(moves: list[MoveRobot]):
    # Initialize piper SDK
    piper = piper_sdk.C_PiperInterface_V2(CAN_PORT)
    piper.ConnectPort()

    try:
        piper.EnableArm(pu.USE_ALL_MOTOR)
        pu.enable_fun(piper=piper)
        piper.MotionCtrl_2(pu.CAN_CTRL_MODE,
                           pu.MOVE_POSITION_MODE,
                           MOVE_SPEED,
                           pu.POS_VELOCITY_MODE)

        # Execute each move sequentially
        for move in moves:
            move_robot_helper(piper, move, wait=False)

        return {"status": "success", "message": "Robot moved successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        piper.DisconnectPort()
        return {"status": "disconnected", "message": "Port disconnected successfully!"}
