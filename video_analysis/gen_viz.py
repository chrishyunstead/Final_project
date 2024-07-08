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
#         "df/heatmap/testMatch_heatmap_df.csv", base_pitch_path
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


## 미디어 지정 말고
# def basic_gen(track_stub_path):
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#
#     with open(track_stub_path, "rb") as load1:
#         tracks = pickle.load(load1)
#     match_id = "testMatch"
#     base_pitch_path = os.path.join(base_dir, "test/img/nuri_futsal.png")
#     heatmap_path_list = TeamHeatmap().gen_team_heatmap(
#         tracks, base_pitch_path, match_id, os.path.join(base_dir, "viz/heatmap_team")
#     )
#
#     hasball_report = PossessionReport(
#         os.path.join(base_dir, "df/heatmap/testMatch_heatmap_df.csv"), base_pitch_path
#     )
#     possession_lmr_path_list = hasball_report.visual_possession(
#         match_id, os.path.join(base_dir, "viz/possession")
#     )
#     possession_dmr_path_list = hasball_report.visual_activate_zone(
#         match_id, os.path.join(base_dir, "viz/possession")
#     )
#     path_dict = {
#         "heatmap_home": os.path.relpath(heatmap_path_list[0]),
#         "heatmap_away": os.path.relpath(heatmap_path_list[1]),
#         "hasball_lmr_home": os.path.relpath(possession_lmr_path_list[0]),
#         "hasball_lmr_away": os.path.relpath(possession_lmr_path_list[1]),
#         "hasball_dmr": os.path.relpath(possession_dmr_path_list[0]),
#     }
#
#     return path_dict
#
#
# if __name__ == "__main__":
#     basic_gen()


def basic_gen(track_stub_path):
    base_dir = settings.BASE_DIR

    with open(track_stub_path, "rb") as load1:
        tracks = pickle.load(load1)
    match_id = "testMatch"
    base_pitch_path = os.path.join(base_dir, "video_analysis/test/img/nuri_futsal.png")
    heatmap_output_dir = os.path.join(base_dir, "video_analysis/viz/heatmap_team")
    possession_output_dir = os.path.join(base_dir, "video_analysis/viz/possession")

    heatmap_path_list = TeamHeatmap().gen_team_heatmap(
        tracks, base_pitch_path, match_id, heatmap_output_dir
    )

    hasball_report = PossessionReport(
        os.path.join(base_dir, f"video_analysis/df/heatmap/{match_id}_heatmap_df.csv"),
        base_pitch_path,
    )
    possession_lmr_path_list = hasball_report.visual_possession(
        match_id, possession_output_dir
    )
    possession_dmr_path_list = hasball_report.visual_activate_zone(
        match_id, possession_output_dir
    )
    path_dict = {
        "heatmap_home": os.path.join(
            "viz/heatmap_team", os.path.basename(heatmap_path_list[0])
        ),
        "heatmap_away": os.path.join(
            "viz/heatmap_team", os.path.basename(heatmap_path_list[1])
        ),
        "hasball_lmr_home": os.path.join(
            "viz/possession", os.path.basename(possession_lmr_path_list[0])
        ),
        "hasball_lmr_away": os.path.join(
            "viz/possession", os.path.basename(possession_lmr_path_list[1])
        ),
        "hasball_dmr": os.path.join(
            "viz/possession", os.path.basename(possession_dmr_path_list[0])
        ),
    }

    return path_dict


if __name__ == "__main__":
    basic_gen()


# def basic_gen(track_stub_path):
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     media_root = settings.MEDIA_ROOT
#
#     with open(track_stub_path, "rb") as load1:
#         tracks = pickle.load(load1)
#     match_id = "testMatch"
#     base_pitch_path = os.path.join(base_dir, "test/img/nuri_futsal.png")
#     heatmap_output_dir = os.path.join(media_root, "viz/heatmap_team")
#     possession_output_dir = os.path.join(media_root, "viz/possession")
#
#     heatmap_path_list = TeamHeatmap().gen_team_heatmap(
#         tracks, base_pitch_path, match_id, heatmap_output_dir
#     )
#
#     hasball_report = PossessionReport(
#         os.path.join(media_root, f"df/heatmap/{match_id}_heatmap_df.csv"),
#         base_pitch_path,
#     )
#     possession_lmr_path_list = hasball_report.visual_possession(
#         match_id, possession_output_dir
#     )
#     possession_dmr_path_list = hasball_report.visual_activate_zone(
#         match_id, possession_output_dir
#     )
#     path_dict = {
#         "heatmap_home": os.path.relpath(heatmap_path_list[0], media_root),
#         "heatmap_away": os.path.relpath(heatmap_path_list[1], media_root),
#         "hasball_lmr_home": os.path.relpath(possession_lmr_path_list[0], media_root),
#         "hasball_lmr_away": os.path.relpath(possession_lmr_path_list[1], media_root),
#         "hasball_dmr": os.path.relpath(possession_dmr_path_list[0], media_root),
#     }
#
#     return path_dict
#
#
# if __name__ == "__main__":
#     basic_gen()
