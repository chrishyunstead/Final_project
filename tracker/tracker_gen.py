from ultralytics import YOLO
import supervision as sv
import pickle
import json
import os
import pandas as pd
import torch
from utils import *


class Tracker:
    def __init__(self, model_path_player=None, model_path_ball=None):
        self.model_player_path = model_path_player
        self.model_ball_path = model_path_ball

    # 선수 객체인식
    def detect_player(self, frames):
        model_player = YOLO(self.model_player_path)
        if torch.cuda.is_available():
            model_player.to("cuda")
        batch_size = 10
        detections = []
        for i in range(0, len(frames), batch_size):
            result = model_player.track(
                frames[i : i + batch_size], conf=0.8, persist=True
            )
            detections += result
        return detections

    # 공 객체인식
    def detect_ball(self, frames):
        model_ball = YOLO(self.model_ball_path)
        if torch.cuda.is_available():
            model_ball.to("cuda")
        batch_size = 10
        detections = []
        for i in range(0, len(frames), batch_size):
            result = model_ball.predict(frames[i : i + batch_size], conf=0.6)
            detections += result
        return detections

    # 선수 : 객체인식 + 트래킹
    # 공 : 객체인식
    def tracks_generator(self, frames, read_stub=False, stub_path=None):
        tracker = sv.ByteTrack(frame_rate=10, track_activation_threshold=0.5)
        if read_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path, "rb") as l:
                tracks = pickle.load(l)
            return tracks

        player_detections = self.detect_player(frames)
        ball_detections = self.detect_ball(frames)
        tracks = {"players": [], "ball": []}  # [{track_id:{'bbox:[x1,y1,x2,y2]}}]
        # 선수
        for frame_num, detection in enumerate(player_detections):
            detection_sv = sv.Detections.from_ultralytics(detection)
            detection_with_tracks = tracker.update_with_detections(detection_sv)
            tracks["players"].append({})
            # 바운딩 박스가 음수일 경우 0으로 대체
            for frame_detection in detection_with_tracks:
                bounding_box = frame_detection[0].tolist()
                for i in range(len(bounding_box)):
                    if bounding_box[i] < 0:
                        bounding_box[i] = 0
                track_id = frame_detection[4]
                coord_frame = get_coordnate(bounding_box)
                tracks["players"][frame_num][track_id] = {
                    "bbox": bounding_box,
                    "coord_frame": coord_frame,
                }
        # 공
        for frame_num, detection in enumerate(ball_detections):
            detection_sv = sv.Detections.from_ultralytics(detection)
            tracks["ball"].append({})
            for frame_detection in detection_sv:
                bounding_box = frame_detection[0].tolist()
                for i in range(len(bounding_box)):
                    if bounding_box[i] < 0:
                        bounding_box[i] = 0
                if len(bounding_box) > 0:
                    coord_frame = get_coordnate(bounding_box)
                    tracks["ball"][frame_num][1] = {
                        "bbox": bounding_box,
                        "coord_frame": coord_frame,
                    }

        if stub_path is not None:
            with open(stub_path, "wb") as s:
                pickle.dump(tracks, s)
        return tracks

    def concat_tracks(self, tracks_left, tracks_right):
        tracks_concat = {"players": [], "ball": []}
        for frame_num, player_tracks in enumerate(tracks_left["players"]):
            tracks_concat["players"].append({})
            tracks_concat["players"][frame_num]["left"] = player_tracks
            tracks_concat["players"][frame_num]["right"] = tracks_right["players"][
                frame_num
            ]
        for frame_num, ball_detection in enumerate(tracks_left["ball"]):
            tracks_concat["ball"].append({})
            tracks_concat["ball"][frame_num]["left"] = ball_detection
            tracks_concat["ball"][frame_num]["right"] = tracks_right["ball"][frame_num]
        return tracks_concat

    def real_tracks_gen(self, tracks):
        tracks_real = {"players": [], "ball": []}
        for object_name, results in tracks.items():
            for frame_num, detections in enumerate(results):
                tracks_real[object_name].append({})
                for pitch_dir, track in detections.items():
                    if track == {}:
                        continue
                    for track_id, values in track.items():
                        coord_tr = values["coord_tr"]
                        if pitch_dir == "left" and coord_tr[0] <= 403:
                            tracks_real[object_name][frame_num][track_id] = values
                        elif pitch_dir == "right" and coord_tr[0] > 403:
                            tracks_real[object_name][frame_num][track_id] = values
        return tracks_real

    def interpolate_ball(self, ball_detections):
        ball_positions = [x.get(1, {}).get("coord_tr", []) for x in ball_detections]
        df_ball_positions = pd.DataFrame(ball_positions, columns=["x", "y"])

        df_ball_positions_itp = df_ball_positions.interpolate()
        df_ball_positions_bf = df_ball_positions_itp.bfill()

        ball_positions_bf = [
            {1: {"coord_tr": x}} for x in df_ball_positions_bf.to_numpy().tolist()
        ]
        return ball_positions_bf
