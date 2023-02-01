import numpy as np
from scipy.spatial.transform import Rotation as R


class ArcBall:
    def __init__(self, NewWidth: float, NewHeight: float):
        self.StVec = np.zeros(3, 'f4')  # Saved click vector
        self.EnVec = np.zeros(3, 'f4')  # Saved drag vector
        self.AdjustWidth = 0.           # Mouse bounds width
        self.AdjustHeight = 0.          # Mouse bounds height
        self.setBounds(NewWidth, NewHeight)
        self.Epsilon = 1.0e-5

    def setBounds(self, NewWidth: float, NewHeight: float):
        assert((NewWidth > 1.0) and (NewHeight > 1.0))
        # Set adjustment factor for width/height
        self.AdjustWidth = 1.0 / ((NewWidth - 1.0) * 0.5)
        self.AdjustHeight = 1.0 / ((NewHeight - 1.0) * 0.5)

    def click(self, NewPt):
        # Map the point to the sphere
        self._mapToSphere(NewPt, self.StVec)

    def drag(self, NewPt):
        NewRot = np.zeros((4,), 'f4')
        # Map the point to the sphere
        self._mapToSphere(NewPt, self.EnVec)
        Perp = np.cross(self.StVec, self.EnVec)
        # Compute the length of the perpendicular vector
        if np.linalg.norm(Perp) > self.Epsilon:  # if its non-zero
            NewRot[:3] = Perp[:3]
            NewRot[3] = np.dot(self.StVec, self.EnVec)
        else:
            pass
        return NewRot

    def _mapToSphere(self, NewPt, NewVec):
        TempPt = NewPt.copy()
        TempPt[0] = (TempPt[0] * self.AdjustWidth) - 1.0
        TempPt[1] = 1.0 - (TempPt[1] * self.AdjustHeight)
        # center
        length2 = np.dot(TempPt, TempPt)
        if length2 > 1.0:
            # Compute a normalizing factor
            norm = 1.0 / np.sqrt(length2)
            NewVec[0] = TempPt[0] * norm
            NewVec[1] = TempPt[1] * norm
            NewVec[2] = 0.0
        else:
            # Return a vector to a point mapped inside the sphere
            NewVec[0] = TempPt[0]
            NewVec[1] = TempPt[1]
            NewVec[2] = np.sqrt(1.0 - length2)


class ArcBallUtil(ArcBall):
    def __init__(self, NewWidth: float, NewHeight: float):
        self.Transform = np.identity(4, 'f4')
        self.LastRot = np.identity(3, 'f4')
        self.ThisRot = np.identity(3, 'f4')
        self.isDragging = False
        super().__init__(NewWidth, NewHeight)

    def onDrag(self, cursor_x, cursor_y):
        if self.isDragging:
            mouse_pt = np.array([cursor_x, cursor_y], 'f4')
            # Update End Vector And Get Rotation As Quaternion
            self.ThisQuat = self.drag(mouse_pt)
            self.ThisQuat[0] *= 0.5  # Reduce the influence of the vertical axis
            self.ThisRot = self.Matrix3fSetRotationFromQuat4f(self.ThisQuat)
            self.ThisRot = np.matmul(self.LastRot, self.ThisRot)
            self.Transform = self.Matrix4fSetRotationFromMatrix3f(
                self.Transform, self.ThisRot)
        return

    def resetRotation(self):
        self.isDragging = False
        self.LastRot = np.identity(3, 'f4')
        self.ThisRot = np.identity(3, 'f4')
        self.Transform = self.Matrix4fSetRotationFromMatrix3f(self.Transform,
                                                              self.ThisRot)

    def onClickLeftUp(self):
        self.isDragging = False
        # Set Last Static Rotation To Last Dynamic One
        self.LastRot = self.ThisRot.copy()

    def onClickLeftDown(self, cursor_x: float, cursor_y: float):
        self.LastRot = self.ThisRot.copy()
        self.isDragging = True
        mouse_pt = np.array([cursor_x, cursor_y], 'f4')
        self.click(mouse_pt)
        return

    @staticmethod
    def Matrix4fSetRotationFromMatrix3f(NewObj, m3x3):
        scale = np.linalg.norm(NewObj[:3, :3], ord='fro') / np.sqrt(3)
        NewObj[0:3, 0:3] = m3x3 * scale
        scaled_NewObj = NewObj
        return scaled_NewObj

    def Matrix3fSetRotationFromQuat4f(self, q1):
        if np.sum(np.dot(q1, q1)) < self.Epsilon:
            return np.identity(3, 'f4')
        r = R.from_quat(q1)
        return r.as_matrix().T
