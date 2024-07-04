from sklearn.cluster import KMeans
import cv2
import numpy as np
import json


class TeamAssigner:
    def __init__(self):
        self.team_color_dict = {}
        self.player_team_dict = {}

    # 1. 2개의 클러스터만 가지는 이미지용 KMeans 클러스터링 모델 생성
    # 1-1. KMeans 클러스터링 모델에 적용하기 위해 이미지 reshape
    def gen_img_kmeans(self, image):
        kmeans = KMeans(n_clusters=2, init="k-means++", n_init=20, random_state=10)
        image_2d = image.reshape(-1, 3)
        kmeans.fit(image_2d)
        return kmeans

    # 1. 단일 프레임에서 선수 유니폼 색 추출
    # 1-1. 단일 프레임에서 바운딩박스를 기준으로 선수 이미지만 로드
    # 1-2. 선수 이미지 색 코드 RGB로 변경
    # 2. 이미지용 KMeans 클러스터링 모델 적용
    # 2-1. 선수 이미지의 모서리들은 배경일 확률이 큼
    # 2-2. 모서리들의 클러스터의 개수를 기준으로 한 선수 이미지의 배경색 클러스터 확인
    # 2-3. 1-(배경 클러스터) => 선수 유니폼 색 클러스터 확인
    # 3. 선수 유니폼 색 클러스터의 cluster_center를 한 선수의 유니폼 색으로 설정
    def get_player_color(self, frame, bounding_box):
        image = frame[
            int(bounding_box[1]) : int(bounding_box[3]),
            int(bounding_box[0]) : int(bounding_box[2]),
        ]
        top_half_img_BGR = image[
            int(image.shape[0] * (0.4)) : int(image.shape[0] * (0.5)),
            int(image.shape[1] * (0.25)) : int(image.shape[1] * (0.75)),
        ]
        top_half_img_Lab = cv2.cvtColor(top_half_img_BGR, cv2.COLOR_BGR2Lab)
        kmeans = self.gen_img_kmeans(top_half_img_Lab)
        clusters = kmeans.labels_.tolist()
        uniform_cls = max(clusters, key=clusters.count)
        player_color_Lab = kmeans.cluster_centers_[uniform_cls]
        return player_color_Lab

    # 1. 단일 프레임에서 선수들의 유니폼 색을 get_player_color함수를 이용해 추출
    # 1-1. 하나의 리스트에 선수들 유니폼 색 append
    # 2. 유니폼 색 리스트를 새로운 KMeans 클러스터링 모델에 적용(2개 클러스터) -> 두 개의 팀으로 분류
    # 2-1. self.kmeans에 팀 분류 KMeans 클러스터링 모델 저장
    # 3. cluster_center를 enumerate해서 self.team_color_dict에 team_id, 팀 색상 저장
    def assign_team_color(self, frame_left, frame_right, player_detections):
        player_colors = []
        for _, player_detection in player_detections.items():
            bounding_box = player_detection["bbox"]
            pitch_side = player_detection["pitch_side"]
            if pitch_side == "left":
                player_color = self.get_player_color(frame_left, bounding_box)
                player_colors.append(player_color)
            else:
                player_color = self.get_player_color(frame_right, bounding_box)
                player_colors.append(player_color)
        kmeans = KMeans(n_clusters=2, init="k-means++", n_init=10, random_state=0)
        kmeans.fit(player_colors)
        self.kmeans = kmeans
        for team_id, team_color in enumerate(kmeans.cluster_centers_):
            self.team_color_dict[team_id] = team_color

    # 1. 단일 프레임에서 선수별로 팀 구분
    # 1-1. self.get_player_color로 한 선수의 유니폼 색 추출
    # 1-2. assign_team_color에서 저장한 kmeans 클러스터링 모델에 유니폼 색을 적용해 클러스터 predict
    # 2. self.player_team_dict에 선수의 track_id(player_id)와 선수의 team_id(player_team) 저장
    def get_player_team(self, frame, player_bbox, player_id):
        if player_id in self.player_team_dict:
            return self.player_team_dict[player_id]
        player_color = self.get_player_color(frame, player_bbox)
        player_team = self.kmeans.predict(np.array(player_color).reshape(1, -1))[0]
        self.player_team_dict[player_id] = player_team
        return player_team

    # 저장된 tracks.pkl에 프레임별 선수의 team_id, team_color 저장
    # 1. 첫 번째 프레임에서 유니폼 색 추출 후 team_id, team_color 생성 후 저장
    # 2. tracks.pkl로 부터 각 프레임 속 선수들의
    def add_2_tracks(self, frames_left, frames_right, tracks):
        self.assign_team_color(frames_left[0], frames_right[0], tracks["players"][0])
        for frame_num, player_tracks in enumerate(tracks["players"]):
            for player_id, track in player_tracks.items():
                if track["pitch_side"] == "left":
                    if track["coord_tr"][0] > 370:
                        continue
                    team_id = self.get_player_team(
                        frames_left[frame_num], track["bbox"], player_id
                    )
                    tracks["players"][frame_num][player_id]["team"] = team_id
                    tracks["players"][frame_num][player_id]["team_color"] = [
                        int(i)
                        for i in cv2.cvtColor(
                            np.array(
                                [[[i for i in self.team_color_dict[team_id]]]],
                                dtype=np.uint8,
                            ),
                            cv2.COLOR_Lab2RGB,
                        ).tolist()[0][0]
                    ]
                else:
                    if track["coord_tr"][0] < 430:
                        continue
                    team_id = self.get_player_team(
                        frames_right[frame_num], track["bbox"], player_id
                    )
                    tracks["players"][frame_num][player_id]["team"] = team_id
                    tracks["players"][frame_num][player_id]["team_color"] = [
                        int(i)
                        for i in cv2.cvtColor(
                            np.array(
                                [[[i for i in self.team_color_dict[team_id]]]],
                                dtype=np.uint8,
                            ),
                            cv2.COLOR_Lab2RGB,
                        ).tolist()[0][0]
                    ]
        return tracks
