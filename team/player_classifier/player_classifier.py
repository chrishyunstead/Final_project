import cv2
import matplotlib.pyplot as plt

class playerClassifier:
    def __init__(self):
        self.left_player_id={}
        self.right_player_id={}

    def player_identifier(self,frame_left,frame_right,tracks):
        for frame_num,player_track in enumerate(tracks['players']):
            for track_id,values in player_track.items():
                if track_id in self.left_player_id.keys():
                    pass
                if values['pitch_side']=='left':
                    self.left_player_id[track_id]=[frame_left[values['bbox']]]
                if values['pitch_side']=='right':
                    self.right_player_id[track_id]=[frame_right[values['bbox']]]