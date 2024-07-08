import os
import pickle

from mysite import settings
from .team_heatmap import TeamHeatmap
from .hasball_report import PossessionReport


# def basic_gen(track_stub_path):
#     with open(track_stub_path, "rb") as load1:
#         tracks = pickle.load(load1)
#     match_id = "testMatch"
#     base_pitch_path = "test/img/nuri_futsal.png"
#     heatmap_path_list = TeamHeatmap().gen_team_heatmap(
#         tracks, base_pitch_path, match_id, "viz/heatmap_team"
#     )
#
#     hasball_report = PossessionReport(
#         "df/heatmap/testMatch-heatmap-df.csv", base_pitch_path
#     )
#     possession_lmr_path_list = hasball_report.visual_possession(
#         match_id, "viz/possession"
#     )
#     possession_dmr_path_list = hasball_report.visual_activate_zone(
#         match_id, "viz/possession"
#     )
#     path_dict = {
#         "heatmap_home": heatmap_path_list[0],
#         "heatmap_away": heatmap_path_list[1],
#         "hasball_lmr_home": possession_lmr_path_list[0],
#         "hasball_lmr_away": possession_lmr_path_list[1],
#         "hasball_dmr": possession_dmr_path_list[0],
#     }
#     # 이미지 경로를 MEDIA_URL 기반으로 변경
#     for key, value in path_dict.items():
#         path_dict[key] = os.path.join("viz", value)
#
#     return path_dict
#
#
# if __name__ == "__main__":
#     basic_gen()

#
# def basic_gen(track_stub_path):
#
#     with open(track_stub_path, "rb") as load1:
#         tracks = pickle.load(load1)
#     match_id = "testMatch"
#     base_pitch_path = "test/img/nuri_futsal.png"
#     heatmap_path_list = TeamHeatmap().gen_team_heatmap(
#         tracks, base_pitch_path, match_id, "viz/heatmap_team"
#     )
#
#     hasball_report = PossessionReport(
#         "df/heatmap/testMatch-heatmap-df.csv",
#         base_pitch_path,
#     )
#     possession_lmr_path_list = hasball_report.visual_possession(
#         match_id, "viz/possession"
#     )
#     possession_dmr_path_list = hasball_report.visual_activate_zone(
#         match_id, "viz/possession"
#     )
#     path_dict = {
#         "heatmap_home": heatmap_path_list[0],
#         "heatmap_away": heatmap_path_list[1],
#         "hasball_lmr_home": possession_lmr_path_list[0],
#         "hasball_lmr_away": possession_lmr_path_list[1],
#         "hasball_dmr": possession_dmr_path_list[0],
#     }
#     for key, value in path_dict.items():
#         path_dict[key] = os.path.join(
#             settings.MEDIA_URL, os.path.relpath(value, settings.MEDIA_ROOT)
#         )
#
#     return path_dict
#
#
# if __name__ == "__main__":
#     basic_gen()


def basic_gen(track_stub_path):

    with open(track_stub_path, "rb") as load1:
        tracks = pickle.load(load1)
    match_id = "testMatch"
    base_pitch_path = os.path.join(
        settings.BASE_DIR, "video_analysis/test/img/nuri_futsal.png"
    )
    heatmap_save_path = os.path.join(settings.MEDIA_ROOT, "viz/heatmap_team")
    heatmap_path_list = TeamHeatmap().gen_team_heatmap(
        tracks, base_pitch_path, match_id, heatmap_save_path
    )

    hasball_report = PossessionReport(
        os.path.join(settings.MEDIA_ROOT, "df/heatmap/testMatch-heatmap-df.csv"),
        base_pitch_path,
    )
    possession_save_path = os.path.join(settings.MEDIA_ROOT, "viz/possession")
    possession_lmr_path_list = hasball_report.visual_possession(
        match_id, possession_save_path
    )
    possession_dmr_path_list = hasball_report.visual_activate_zone(
        match_id, possession_save_path
    )
    path_dict = {
        "heatmap_home": os.path.join(
            settings.MEDIA_URL,
            os.path.relpath(heatmap_path_list[0], settings.MEDIA_ROOT),
        ),
        "heatmap_away": os.path.join(
            settings.MEDIA_URL,
            os.path.relpath(heatmap_path_list[1], settings.MEDIA_ROOT),
        ),
        "hasball_lmr_home": os.path.join(
            settings.MEDIA_URL,
            os.path.relpath(possession_lmr_path_list[0], settings.MEDIA_ROOT),
        ),
        "hasball_lmr_away": os.path.join(
            settings.MEDIA_URL,
            os.path.relpath(possession_lmr_path_list[1], settings.MEDIA_ROOT),
        ),
        "hasball_dmr": os.path.join(
            settings.MEDIA_URL,
            os.path.relpath(possession_dmr_path_list[0], settings.MEDIA_ROOT),
        ),
    }

    return path_dict


if __name__ == "__main__":
    basic_gen()
