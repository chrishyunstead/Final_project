import os
import pickle
from .tracker import Tracker
from .team_assigner import TeamAssigner
from .player_ball_assigner import BallAssigner
from .perspective_changer import PerspectiveChanger
from .video_2_frames import Video2frames


# def tracking(left_path, right_path):
#     # 영상 불러오기
#     """frames_left=read_video('input-video/test-left-1q.mp4')
#     frames_right=read_video('input-video/test-right-1q.mp4')[10:]
#     min_frame_len=min(len(frames_left),len(frames_right))
#     frames_left=frames_left[:min_frame_len]
#     frames_right=frames_right[:min_frame_len]"""
#     video_path_left = left_path
#     pic_path_left = "input-pic/1q/left"
#     video_path_right = right_path
#     pic_path_right = "input-pic/1q/right"
#     frames_path = "test"
#     v2f = Video2frames(frames_path)
#     frame_dict = v2f.get_1fps(
#         pic_path_left, pic_path_right, video_path_left, video_path_right
#     )
#     frames_left = frame_dict["left"]
#     frames_right = frame_dict["right"]
#
#     # 트래커 클래스 시작
#     model_path_player = "model/best_player_detector.pt"
#     model_path_ball = "model/best_ball_detector.pt"
#     tracker = Tracker(model_path_player, model_path_ball)
#     track_stub_path_left = "track_stub/twp_tracks_left_1.pkl"
#     track_stub_path_right = "track_stub/twp_tracks_right_1.pkl"
#
#     # 트래킹 결과 생성
#     tracks_left = tracker.tracks_generator(
#         frames_left, read_stub=True, stub_path=track_stub_path_left
#     )
#     tracks_right = tracker.tracks_generator(
#         frames_right, read_stub=True, stub_path=track_stub_path_right
#     )
#     tracks = tracker.concat_tracks(tracks_left, tracks_right)
#
#     # homography 적용
#     homography_json_path = "test/homography_dict.json"
#     homograph_adapter = PerspectiveChanger(homography_json_path)
#     tracks_changed = homograph_adapter.perspective_transformer(tracks)
#
#     # real tracks gen
#     tracks_tr = tracker.real_tracks_gen(tracks_changed)
#
#     # interpolate missing ball postion
#     tracks_tr["ball"] = Tracker().interpolate_ball(tracks_tr["ball"])
#
#     # 유니폼 색 기반 팀 구분
#     tracks_assigned = TeamAssigner().add_2_tracks(frames_left, frames_right, tracks_tr)
#
#     # assign ball aquisition
#     tracks_assigned_2 = BallAssigner().add_2_tracks(tracks_assigned)
#
#     with open("track_stub/twp_tracks_1.pkl", "wb") as s1:
#         pickle.dump(tracks_assigned_2, s1)
#
#     return "track_stub/twp_tracks_1.pkl"
#
#
# if __name__ == "__main__":
#     tracking()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def tracking(left_path, right_path):
    # 영상 불러오기
    video_path_left = left_path
    pic_path_left = os.path.join(BASE_DIR, "input-pic", "1q", "left")
    video_path_right = right_path
    pic_path_right = os.path.join(BASE_DIR, "input-pic", "1q", "right")
    frames_path = os.path.join(BASE_DIR, "test")
    v2f = Video2frames(frames_path)
    frame_dict = v2f.get_1fps(
        pic_path_left, pic_path_right, video_path_left, video_path_right
    )
    frames_left = frame_dict["left"]
    frames_right = frame_dict["right"]

    # 트래커 클래스 시작
    model_path_player = os.path.join(BASE_DIR, "model", "best_player_detector.pt")
    model_path_ball = os.path.join(BASE_DIR, "model", "best_ball_detector.pt")
    tracker = Tracker(model_path_player, model_path_ball)
    track_stub_path_left = os.path.join(BASE_DIR, "track_stub", "twp_tracks_left_1.pkl")
    track_stub_path_right = os.path.join(
        BASE_DIR, "track_stub", "twp_tracks_right_1.pkl"
    )

    # 트래킹 결과 생성
    tracks_left = tracker.tracks_generator(
        frames_left, read_stub=True, stub_path=track_stub_path_left
    )
    tracks_right = tracker.tracks_generator(
        frames_right, read_stub=True, stub_path=track_stub_path_right
    )
    tracks = tracker.concat_tracks(tracks_left, tracks_right)

    # homography 적용
    homography_json_path = os.path.join(BASE_DIR, "test", "homography_dict.json")
    homograph_adapter = PerspectiveChanger(homography_json_path)
    tracks_changed = homograph_adapter.perspective_transformer(tracks)

    # real tracks gen
    tracks_tr = tracker.real_tracks_gen(tracks_changed)

    # interpolate missing ball postion
    tracks_tr["ball"] = Tracker().interpolate_ball(tracks_tr["ball"])

    # 유니폼 색 기반 팀 구분
    tracks_assigned = TeamAssigner().add_2_tracks(frames_left, frames_right, tracks_tr)

    # assign ball aquisition
    tracks_assigned_2 = BallAssigner().add_2_tracks(tracks_assigned)

    os.makedirs(os.path.join(BASE_DIR, "track_stub"), exist_ok=True)
    with open(os.path.join(BASE_DIR, "track_stub", "twp_tracks_1.pkl"), "wb") as s1:
        pickle.dump(tracks_assigned_2, s1)

    return os.path.join(BASE_DIR, "track_stub", "twp_tracks_1.pkl")


if __name__ == "__main__":
    tracking()
