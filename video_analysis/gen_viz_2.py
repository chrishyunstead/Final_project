import pickle
import matplotlib.pyplot as plt
from video_analysis.team_heatmap import TeamHeatmap
from passmap import PassMap
from video_analysis.hasball_report import PossessionReport
from stats_gen import statGenerator


def main(track_stub_path):
    with open(track_stub_path, "rb") as load1:
        tracks = pickle.load(load1)
    match_id = "testMatch"
    base_pitch_path = "test/img/nuri_futsal.png"
    heatmap_path_list = TeamHeatmap().gen_team_heatmap(
        tracks, base_pitch_path, match_id, "viz/heatmap_team"
    )

    passmap = PassMap(f"track-stub/{match_id}-track-stub.pkl", base_pitch_path)
    passmap.players_withball_data()
    passmap.player_average_coord()
    passmap.create_passmap_data(match_id, "df/passmap")
    passmap_path_list = passmap.passmap_plot("viz/passmap", match_id)

    hasball_report = PossessionReport(
        "df/heatmap/testMatch_heatmap_df.csv", base_pitch_path
    )
    possession_lmr_path_list = hasball_report.visual_possession(
        match_id, "viz/possession"
    )
    possession_dmr_path_list = hasball_report.visual_activate_zone(
        match_id, "viz/possession"
    )

    stat_gen = statGenerator(f"track-stub/{match_id}-track-stub.pkl")
    speed_dist_stats_df = stat_gen.calc_speed_dist("df/stats", match_id)
    pass_stats_df = stat_gen.calc_pass(match_id)

    stat_gen.merge_stats(speed_dist_stats_df, pass_stats_df, "df/stats", match_id)


if __name__ == "__main__":
    main()
