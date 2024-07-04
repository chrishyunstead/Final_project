import pickle
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib import font_manager, rc
import os
from glob import glob

class PassMap:
    def __init__(self,stub_path,base_pitch_path):
        with open(stub_path,'rb') as load:
            self.tracks=pickle.load(load)
        self.base_pitch=mpimg.imread(base_pitch_path)
        self.data = None
        self.df_players_with_ball = None
        self.df_passmap_success = None
        self.df_passmap_fail = None
        self.df_passmap_bbox = None
    
    def players_withball_data(self):
        tracks=self.tracks
        players_with_ball = []
        for frame_num,playaer_tracks in enumerate(tracks['players']):
            for player_id, player_info in playaer_tracks.items():
                if player_info.get('has_ball'):
                    players_with_ball.append({
                    'frame': frame_num,
                    'player_initial': player_id,
                    'player_name': player_info['kr_name'],
                    'team': player_info['team'],
                    'team_color':player_info['team_color'],
                    'coord_tr': player_info['coord_tr'],
                    'start_pitch_side':player_info['start_pitch_side']
                    })
        self.df_players_with_ball = pd.DataFrame(players_with_ball)
                                                
    def player_average_coord(self):
        pass_player_name = self.df_players_with_ball['player_name'].unique().tolist()
        passmap_bbox = []
        for player_name in pass_player_name:
            coord_data = self.df_players_with_ball[self.df_players_with_ball['player_name'] == player_name]['coord_tr'].tolist()
            coord_average = [(sum(item)/len(item)) for item in zip(*coord_data)]
            passmap_bbox.append({
                'player_name': player_name,
                'team': self.df_players_with_ball[self.df_players_with_ball['player_name'] == player_name]['team'].tolist()[0],
                'coord_average': coord_average,
                'coord_average_x': coord_average[0],
                'coord_average_y': coord_average[1],
            })
        self.df_passmap_bbox = pd.DataFrame(passmap_bbox)
    
    def create_passmap_data(self,match_id:str,pass_df_path:str):
        if not os.path.exists(pass_df_path):
            print('dir for pass df not exists\nmaking dir...')
            os.mkdir(pass_df_path)
            print('dir for pass df created!')
        else:
            print('dir for pass df exists!')
            if len(glob(pass_df_path+f"/{match_id}*"))==2:
                print('pass df already exists!')
                self.df_passmap_success=pd.read_csv(pass_df_path+f"/{match_id}-pass-success-df.csv")
                self.df_passmap_fail=pd.read_csv(pass_df_path+f"/{match_id}-pass-fail-df.csv")
        passmap_success = []
        passmap_fail = []
        players_with_ball = self.df_players_with_ball.to_dict('records')
        print('making pass dataframe...')
        for i in range(len(players_with_ball) - 1):
            if players_with_ball[i]['team'] == players_with_ball[i + 1]['team']:
                if players_with_ball[i]['player_name'] != players_with_ball[i + 1]['player_name']:
                    passmap_success.append({
                        'frame': players_with_ball[i]['frame'],
                        'passer_name': players_with_ball[i]['player_name'],
                        'passer_initial': players_with_ball[i]['player_initial'],
                        'passer_coord': players_with_ball[i]['coord_tr'],
                        'receiver_name': players_with_ball[i + 1]['player_name'],
                        'receiver_initial': players_with_ball[i + 1]['player_initial'],
                        'receiver_coord': players_with_ball[i + 1]['coord_tr'],
                        'team': players_with_ball[i]['team'],
                        'team_color':players_with_ball[i]['team_color'],
                        'start_pitch_side':players_with_ball[i]['start_pitch_side']
                    })
            else:
                passmap_fail.append({
                    'frame': players_with_ball[i]['frame'],
                    'passer_name': players_with_ball[i]['player_name'],
                    'passer_initial': players_with_ball[i]['player_initial'],
                    'passer_coord': players_with_ball[i]['coord_tr'],
                    'interceptor_name': players_with_ball[i + 1]['player_name'],
                    'interceptor_initial': players_with_ball[i + 1]['player_initial'],
                    'interceptor_coord': players_with_ball[i + 1]['coord_tr'],
                    'passer_team': players_with_ball[i]['team'],
                    'interceptor_team': players_with_ball[i + 1]['team']
                })
        
        for i in passmap_success:
            i['passer_x'] = self.df_passmap_bbox[self.df_passmap_bbox['player_name'] == i['passer_name']]['coord_average_x'].item()
            i['passer_y'] = self.df_passmap_bbox[self.df_passmap_bbox['player_name'] == i['passer_name']]['coord_average_y'].item()
            i['receiver_x'] = self.df_passmap_bbox[self.df_passmap_bbox['player_name'] == i['receiver_name']]['coord_average_x'].item()
            i['receiver_y'] = self.df_passmap_bbox[self.df_passmap_bbox['player_name'] == i['receiver_name']]['coord_average_y'].item()

        for i in passmap_fail:
            i['passer_x'] = self.df_passmap_bbox[self.df_passmap_bbox['player_name'] == i['passer_name']]['coord_average_x'].item()
            i['passer_y'] = self.df_passmap_bbox[self.df_passmap_bbox['player_name'] == i['passer_name']]['coord_average_y'].item()
            i['interceptor_x'] = self.df_passmap_bbox[self.df_passmap_bbox['player_name'] == i['interceptor_name']]['coord_average_x'].item()
            i['interceptor_y'] = self.df_passmap_bbox[self.df_passmap_bbox['player_name'] == i['interceptor_name']]['coord_average_y'].item()

        self.df_passmap_success = pd.DataFrame(passmap_success)
        self.df_passmap_success.to_csv(f"{pass_df_path}/{match_id}-pass-success-df.csv")
        self.df_passmap_fail = pd.DataFrame(passmap_fail)
        self.df_passmap_fail.to_csv(f"{pass_df_path}/{match_id}-pass-fail-df.csv")
    
    def passmap_plot(self,passmap_viz_path:str,match_id:str):
        if not os.path.exists(passmap_viz_path):
            print('no dir for passmap viz\nmaking dir...')
            os.mkdir(passmap_viz_path)
            print('dir for passmap viz created!')
        else:
            print('dir exists')
            if len(glob(passmap_viz_path+f"/{match_id}*"))==2:
                print('pass map viz already exists!')
                return glob(passmap_viz_path+f"{match_id}*")
        print('making passmap vizs...')
        plt.rcParams['axes.unicode_minus'] = False
        f_path = "font/malgun.ttf"
        font_name = font_manager.FontProperties(fname=f_path).get_name()
        rc('font', family=font_name)
        df_passmap=self.df_passmap_success
        df_passmap_split={'Team-A':df_passmap.query("start_pitch_side=='left'"),
                          'Team-B':df_passmap.query("start_pitch_side=='right'")}
        for team,df_passmap in df_passmap_split.items():
            img = self.base_pitch.copy()
            plt.figure()
            plt.imshow(img)
            plt.axis('off')


            pass_counts = df_passmap.groupby('passer_name').size().to_dict()
            max_pass_counts = max([i for _, i in pass_counts.items()])

            for idx, row in df_passmap.iterrows():
                passer_x = row['passer_x']
                passer_y = row['passer_y']
                receiver_x = row['receiver_x']
                receiver_y = row['receiver_y']
                team_color = [i/255 for i in row['team_color']]
                
                passer_count = pass_counts.get(row['passer_name'], 1)
                receiver_count = pass_counts.get(row['receiver_name'], 1)
                linewidth = (passer_count + receiver_count) * 0.5
                
                plt.plot([passer_x, receiver_x], [passer_y, receiver_y], color=team_color, alpha=0.25, linewidth=linewidth)
                
                passer_size = (passer_count / max_pass_counts) * 600
                receiver_size = (receiver_count / max_pass_counts) * 600
                plt.scatter(passer_x, passer_y, color='white', edgecolors='black', marker='o', s=passer_size, label=row['passer_name'], zorder=2)
                plt.scatter(receiver_x, receiver_y, color='white', edgecolors='black', marker='o', s=receiver_size, label=row['receiver_name'], zorder=2)

            avg_positions = df_passmap.groupby('passer_name')[['passer_x', 'passer_y']].mean()
            for idx, row in avg_positions.iterrows():
                avg_x = row['passer_x']
                avg_y = row['passer_y']
                plt.text(avg_x, avg_y - 50, idx, fontsize=10, fontweight='bold', ha='center', va='top', color='black', zorder=3)
            if team=='Team-A':
                output_path = passmap_viz_path+f"/{match_id}-passmap-team_a.png"
            else:
                output_path = passmap_viz_path+f"/{match_id}-passmap-team_b.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print('passmap viz created!')
        return glob(passmap_viz_path+f"{match_id}*")