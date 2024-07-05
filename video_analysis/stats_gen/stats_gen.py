import cv2
import sys 
import pandas as pd
import pickle
import os
from glob import glob

class statGenerator:
    def __init__(self,stub_path:str):
        with open (stub_path,'rb') as load:
            self.tracks=pickle.load(load)
        self.frame_window=5
        self.frame_rate=10
    
    # 속도,거리 정보를 tracks.pkl파일에 추가
    def speed_distance_to_tracks(self):
        # 객체와 트랙 정보를 이용하여 주어진 프레임 윈도우 내에서 속도와 이동 거리를 계산
        # 바운딩 박스를 이용해 객체의 시작과 끝 위치를 구하고, 이를 실제 거리 단위로 변환한 후 속도와 거리를 계산하여 트랙에 추가
        tracks=self.tracks
        total_distance = {}
       
        for object, object_tracks in tracks.items():
            if object == "ball":
                continue 
            number_of_frames = len(object_tracks)
            for frame_num in range(0, number_of_frames, self.frame_window):
                last_frame = min(frame_num + self.frame_window, number_of_frames - 1)

                for track_id, _ in object_tracks[frame_num].items():
                    if track_id not in object_tracks[last_frame]:
                        continue

                    start_position = object_tracks[frame_num][track_id]['coord_tr']
                    end_position = object_tracks[last_frame][track_id]['coord_tr']
                    
                    if start_position is None or end_position is None:
                        continue

                    # 픽셀 단위를 실제 거리 단위로 변환
                    distance_covered_x = (end_position[0] - start_position[0])/40
                    distance_covered_y = (end_position[1] - start_position[1])/40
                    distance_covered = (distance_covered_x**2 + distance_covered_y**2)**0.5 # 미터 단위

                    time_elapsed = (last_frame - frame_num) / self.frame_rate
                    speed_meters_per_second = distance_covered / time_elapsed
                    speed_km_per_hour = (speed_meters_per_second)*3.6

                    if object not in total_distance:
                        total_distance[object] = {}
                    
                    if track_id not in total_distance[object]:
                        total_distance[object][track_id] = 0
                    
                    total_distance[object][track_id] += distance_covered

                    for frame_num_batch in range(frame_num, last_frame):
                        if track_id not in tracks[object][frame_num_batch]:
                            continue
                        tracks[object][frame_num_batch][track_id]['speed'] = speed_km_per_hour
                        tracks[object][frame_num_batch][track_id]['distance'] = total_distance[object][track_id]
        return tracks
    
    # pickle to dataframe(속도 & 거리) - raw data 생성 / 저장
    def speed_dist_pkl_2_df(self,save_path:str,match_id:str):
        spddst_path=f"{save_path}/{match_id}-speed_dist-raw.csv"
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        else:
            if len(glob(spddst_path.split('.')[0]+'*'))==1:
                df=pd.read_csv(spddst_path,index_col=0)
                return df
        tracks_spddst=self.speed_distance_to_tracks()
        players_speed_distance=[]
        for frame_num in range(len(tracks_spddst['players'])-1):
            for player_id,player_info in tracks_spddst['players'][frame_num].items():
                players_speed_distance.append({
                    'frame':frame_num,
                    'player_initial': player_id,
                    'player_name': player_info['kr_name'],
                    'team': player_info['team'],
                    'player_speed(km/h)': player_info['speed'],
                    'distance(m)': player_info['distance']})
        df=pd.DataFrame(players_speed_distance)
        df.to_csv(spddst_path)
        return df
    
    # 속도, 거리 스탯 생성
    def calc_speed_dist(self,save_path:str,match_id:str):
        spdst_df=self.speed_dist_pkl_2_df(save_path,
                                          match_id)
        pass_player_name = spdst_df['player_name'].unique().tolist()
        player_stat = []
        for player_name in pass_player_name:
            player_team = spdst_df[spdst_df['player_name'] == player_name]['team'].tolist()[0]
            speed_data = spdst_df[spdst_df['player_name'] == player_name]['player_speed(km/h)'].tolist()
            speed_average = sum(speed_data)/len(speed_data)
            speed_max = max(speed_data)/1.5 # 영상을 10 frame 단위로 사용하여, 보정값 1.5로 나누어줌
            distance = round(max(spdst_df[spdst_df['player_name'] == player_name]['distance(m)'].tolist()),2)
            player_stat.append({
                'player_name': player_name,
                'team': player_team,
                'average_speed(km/h)': speed_average,
                'max_speed(km/h)': speed_max,
                'total_distance(m)': distance,
                })
        df_calc = pd.DataFrame(player_stat)
        df_calc.to_csv(f"df/stats/{match_id}-speed_dist-stats.csv")
        return df_calc
    
    # 패스 스탯 생성
    def calc_pass(self,match_id:str):
        df_passmap_success=pd.read_csv(f"df/passmap/{match_id}-pass-success-df.csv",
                                       index_col=0)
        df_passmap_fail=pd.read_csv(f"df/passmap/{match_id}-pass-fail-df.csv",
                                       index_col=0)
        
        pass_success_count=df_passmap_success['passer_name'].value_counts()
        pass_success_count.name='pass_success_count'

        pass_fail_count=df_passmap_fail['passer_name'].value_counts()
        pass_fail_count.name='pass_fail_count'

        pass_intercept_count = df_passmap_fail['interceptor_name'].value_counts()
        pass_intercept_count.name = 'pass_intercept_count'

        # 두 Series를 DataFrame으로 결합
        df_combined = pd.concat(
            [pass_success_count, pass_fail_count, pass_intercept_count],axis=1)

        # NaN 값을 0으로 대체
        df_pass_count = df_combined.fillna(0)

        df_pass_count['pass_success_rate(%)'] = round(
            (df_pass_count['pass_success_count'] / 
             (df_pass_count['pass_success_count'] + df_pass_count['pass_fail_count'])) * 100, 2)

        df_pass_count_sorted = df_pass_count.sort_values(by='pass_success_rate(%)', ascending=False).reset_index()
        df_pass_count_sorted.rename({'index':'player_name'},axis=1,inplace=True)
        df_pass_count_sorted.to_csv(f"df/stats/{match_id}-pass-stats.csv")
        return df_pass_count_sorted
    
    def merge_stats(self,speed_dist_stat_df,pass_stat_df,save_path:str,match_id:str):
        stat_df=speed_dist_stat_df.merge(pass_stat_df,on='player_name')
        stat_df.to_csv(f"{save_path}/{match_id}-stats.csv")
        return stat_df