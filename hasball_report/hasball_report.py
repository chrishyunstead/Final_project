import pandas as pd
import matplotlib.pyplot as plt
import os
from glob import glob


class PossessionReport:
    def __init__(self, df_path: str, base_pitch_path: str):
        self.player_data = pd.read_csv(df_path, index_col=0).query("has_ball==True")
        self.base_pitch = plt.imread(base_pitch_path)

    # 리포트를 위한 데이터프레임 생성
    def create_possession_frame(self):
        player_data = self.player_data

        # 팀 구분
        team_a = player_data.query("start_pitch_side=='left'")
        team_b = player_data.query("start_pitch_side=='right'")

        # 구역별 점유율(가로 기준)
        categories = ["Left Side", "Middle", "Right Side"]
        team_a["region_y"] = pd.cut(
            team_a["coord_y"], bins=[0, 140, 280, 420], labels=categories, ordered=True
        )
        team_b["region_y"] = pd.cut(
            team_b["coord_y"],
            bins=[0, 140, 280, 420],
            labels=categories[::-1],
            ordered=True,
        )

        team_a_y = (
            team_a["region_y"].value_counts(normalize=True).reindex(categories) * 100
        )
        team_b_y = (
            team_b["region_y"].value_counts(normalize=True).reindex(categories[::-1])
            * 100
        )

        # 구역별 점유율(세로 기준)
        team_a["region_x"] = pd.cut(
            team_a["coord_x"], bins=[0, 270, 540, 810], labels=categories, ordered=True
        )

        team_b["region_x"] = pd.cut(
            team_b["coord_x"],
            bins=[0, 270, 540, 810],
            labels=categories[::-1],
            ordered=True,
        )

        team_a_x = (
            team_a["region_x"].value_counts(normalize=True).reindex(categories) * 100
        )  # 영역 비율 계산
        team_b_x = (
            team_b["region_x"].value_counts(normalize=True).reindex(categories[::-1])
            * 100
        )

        # 데이터 프레임 생성
        team_a_df = pd.DataFrame(
            {"Y_Proportion": team_a_y.values, "X_Proportion": team_a_x.values}
        )

        team_b_df = pd.DataFrame(
            {"Y_Proportion": team_b_y.values, "X_Proportion": team_b_x.values}
        )
        return team_a_df, team_b_df

    # 점유율 시각화 리포트 생성 및 저장
    # 구역별 점유율 시각화 (가로 기준)
    def visual_possession(self, match_id: str, save_path: str):
        if not os.path.exists(save_path):
            print("no dir for possession report 1\nmaking dir for possession report 1")
            os.makedirs(save_path)
            print("dir for possession report 1 created!")
        if len(glob(save_path + f"/{match_id}*")) == 2:
            print("possession_report already exist!")
            return glob(save_path + f"/{match_id}-possession-lmr*")
        else:
            print("making possession report 1...")
            play_data_team_a, play_data_team_b = self.create_possession_frame()
            play_data_split = {"Team-A": play_data_team_a, "Team-B": play_data_team_b}
            for team_name, team_data in play_data_split.items():
                nuri_pitch = self.base_pitch.copy()
                fig, ax = plt.subplots()

                # 막대 너비 및 최대 길이 설정
                bar_height = 70
                max_length = 500
                bar_spacing = 130
                labels = ["Left Side", "Middle", "Right Side"]

                # Y_Proportion 값만 사용
                y_proportions = team_data["Y_Proportion"]
                swapped_distribution = y_proportions[
                    ::-1
                ]  # Right Side와 Left Side 위치 바꾸기

                # 막대 그래프 그리기
                for idx, value in enumerate(swapped_distribution):
                    y_start = 35 + (idx * bar_spacing)
                    length = (value / 100) * max_length
                    if team_name == "Team-A":
                        idx = -(idx + 1)
                        ax.barh(
                            y_start,
                            length,
                            height=bar_height,
                            left=402,
                            color="#FB876E",
                            align="edge",
                        )
                        ax.text(
                            280, y_start + 32, labels[idx], va="center", fontsize=10
                        )
                        ax.text(
                            420, y_start + 30, f"{value:.1f}%", va="center", fontsize=11
                        )
                    else:
                        ax.barh(
                            y_start,
                            -length,
                            height=bar_height,
                            left=402,
                            color="#7DB7DA",
                            align="edge",
                        )
                        ax.text(
                            420, y_start + 32, labels[idx], va="center", fontsize=10
                        )
                        ax.text(
                            300, y_start + 30, f"{value:.1f}%", va="center", fontsize=11
                        )

                    if idx < len(swapped_distribution) - 1:
                        ax.axhline(
                            y=y_start + 90,
                            xmin=0.01,
                            xmax=5,
                            color="#BCBCBC",
                            linestyle="--",
                        )

                ax.imshow(nuri_pitch, extent=[2.5, 802.5, 2.5, 402.5])
                ax.axis("off")
                plt.savefig(
                    f"{save_path}/{match_id}-possession-lmr-{team_name}.png",
                    dpi=300,
                    bbox_inches="tight",
                )
            print("possession report 1 created!")
            return glob(save_path + f"/{match_id}-possession-lmr*")

    # 구역별 점유율 시각화 (세로 기준)
    def visual_activate_zone(self, match_id: str, save_path: str):
        if len(glob(f"{save_path}/{match_id}-possession-dma.png")) == 1:
            print("possession report 2 already exists!")
            return glob(f"{save_path}/{match_id}-possession-dma.png")
        print("no viz of possession report 2\nmaking viz of possession report 2...")
        nuri_pitch = self.base_pitch
        team_a_data, team_b_data = self.create_possession_frame()

        fig, ax = plt.subplots()

        # 막대 너비 및 최대 길이 설정
        bar_width = 60
        max_length = 500  # 막대 최대 길이 설정
        bar_spacing = 220
        base_line = 180  # 기준선 설정 (축구장의 하단에 맞추기 위해 Y 좌표를 사용)

        x_proportions_a = team_a_data["X_Proportion"]
        x_proportions_b = team_b_data["X_Proportion"]

        # 팀 A 막대 그래프 그리기
        for idx, value in enumerate(x_proportions_a):
            x_start = base_line + (idx * bar_spacing)  # 막대 시작 위치 x 좌표
            length = (value / 100) * max_length  # 막대 길이 설정
            ax.bar(
                x_start - bar_width,
                length,
                width=bar_width,
                bottom=5,
                color="#FB876E",
                align="edge",
            )  # 막대 그리기
            ax.text(
                x_start - bar_width / 2,
                length + 10,
                f"{value:.1f}%",
                ha="center",
                va="bottom",
                fontsize=12,
            )  # 비율 텍스트
            if idx < len(team_a_data) - 1:
                ax.axvline(
                    x=x_start + bar_width + 45,
                    color="#BCBCBC",
                    linestyle="--",
                    ymin=0.02,
                    ymax=0.99,
                )

        # 팀 B 막대 그래프 그리기
        for idx, value in enumerate(x_proportions_b):
            x_start = base_line + (idx * bar_spacing)  # 막대 시작 위치 x 좌표
            length = (value / 100) * max_length  # 막대 길이 설정
            ax.bar(
                x_start,
                length,
                width=bar_width,
                bottom=5,
                color="#7DB7DA",
                align="edge",
            )  # 막대 그리기
            ax.text(
                x_start + bar_width / 2,
                length + 10,
                f"{value:.1f}%",
                ha="center",
                va="bottom",
                fontsize=12,
            )  # 비율 텍스트

        # 활동 구역 텍스트 추가
        ax.text(170, 425, "Home Third", ha="center", va="center", fontsize=11)
        ax.text(400, 425, "Middle Third", ha="center", va="center", fontsize=11)
        ax.text(610, 425, "Away Third", ha="center", va="center", fontsize=11)

        ax.imshow(nuri_pitch, extent=[2.5, 802.5, 2.5, 402.5])
        ax.axis("off")
        plt.savefig(
            f"{save_path}/{match_id}-possession-dma.png", dpi=300, bbox_inches="tight"
        )
        print("viz of possession report created!")
        return glob(f"{save_path}/{match_id}-possession-dma.png")
