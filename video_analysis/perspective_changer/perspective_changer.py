import numpy as np
import cv2
import json
import pickle


class PerspectiveChanger:
    def __init__(self, homography_dict_path):
        with open(homography_dict_path, "r") as load_l:
            homography = json.load(load_l)
        for pitch_dir, keypoints in homography.items():
            homography[pitch_dir] = np.array(keypoints)
        self.homography_dict = homography

    def perspective_transformer(self, tracks):
        for frame_num, player_tracks in enumerate(tracks["players"]):
            for pitch_dir, players in player_tracks.items():
                for track_id, values in players.items():
                    coord_frame = values["coord_frame"]
                    if pitch_dir == "left":
                        coord_tr = cv2.perspectiveTransform(
                            np.array([np.float32([coord_frame])]),
                            np.float32(self.homography_dict["left_homography"]),
                        )
                        coord_tr = [int(i) for i in coord_tr.tolist()[0][0]]
                        values["coord_tr"] = coord_tr
                        values["pitch_side"] = "left"
                    else:
                        coord_tr = cv2.perspectiveTransform(
                            np.array([np.float32([coord_frame])]),
                            np.float32(self.homography_dict["right_homography"]),
                        )
                        coord_tr = [int(i) for i in coord_tr.tolist()[0][0]]
                        values["coord_tr"] = coord_tr
                        values["pitch_side"] = "right"
        for frame_num, ball_tracks in enumerate(tracks["ball"]):
            for pitch_dir, ball in ball_tracks.items():
                if ball == {}:
                    continue
                for _, values in ball.items():
                    coord_frame = values["coord_frame"]
                    if pitch_dir == "left":
                        coord_tr = cv2.perspectiveTransform(
                            np.array([np.float32([coord_frame])]),
                            np.float32(self.homography_dict["left_homography"]),
                        )
                        coord_tr = [int(i) for i in coord_tr.tolist()[0][0]]
                        values["coord_tr"] = coord_tr
                        values["pitch_side"] = "left"
                    elif pitch_dir == "right":
                        coord_tr = cv2.perspectiveTransform(
                            np.array([np.float32([coord_frame])]),
                            np.float32(self.homography_dict["right_homography"]),
                        )
                        coord_tr = [int(i) for i in coord_tr.tolist()[0][0]]
                        values["coord_tr"] = coord_tr
                        values["pitch_side"] = "right"
        return tracks
