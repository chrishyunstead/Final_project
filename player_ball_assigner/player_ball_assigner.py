import sys
from utils import *


class BallAssigner:
    def __init__(self):
        self.max_distance = 55

    def assign_ball_to_player(self, players, ball_coord):
        min_distance = 99999
        assigned_player = -1
        dist_dict = {}
        for player_id, player in players.items():
            player_coord = player["coord_tr"]
            # player_width=get_bbox_width(player_bbox)
            # distance=measure_distance(player_postion,ball_position)
            # dist_list.append(distance)
            # distance=min(dist_list)
            """distane_left=measure_distance((player_bbox[0]+player_width*(4/10),
                                           player_bbox[-1]),ball_position)
            distane_right=measure_distance((player_bbox[2]-player_width*(4/10),
                                            player_bbox[-1]),ball_position)"""
            distance = measure_distance(player_coord, ball_coord)
            dist_dict[distance] = player_id

        distance_min = min(dist_dict)
        if distance_min < self.max_distance:
            assigned_player = dist_dict[distance_min]
        return assigned_player

    def add_2_tracks(self, tracks):
        for frame_num, player_track in enumerate(tracks["players"]):
            ball_coord = tracks["ball"][frame_num][1]["coord_tr"]
            assigned_player = self.assign_ball_to_player(player_track, ball_coord)
            if assigned_player != -1:
                tracks["players"][frame_num][assigned_player]["has_ball"] = True
        return tracks
