from urdfpy import URDF
import numpy as np
import os
import warnings


class URDF_load:
    def __init__(self, urdf_file: str):
        self.urdf_file: str = urdf_file
        self.rocket: URDF = self.load_urdf()

    def load_urdf(self) -> URDF:
        if not os.path.isfile(self.urdf_file):
            raise ValueError(f"file not found: {self.urdf_file}")
        urdf: URDF = URDF.load(self.urdf_file)
        return urdf

    @staticmethod
    def normalize(value: float) -> float:
        norm = np.linalg.norm(value)
        if norm == 0:
            warnings.warn("trynna normalize a 0 vector")
            return value
        return value / norm

    def print_urdf_file(self):
        for link in self.rocket.links:
            print(link.name)
        for joint in self.rocket.joints:
            print('{} connects {} to {}'.format(joint.name, joint.parent, joint.child))
