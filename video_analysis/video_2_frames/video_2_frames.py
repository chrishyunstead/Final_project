import cv2
import os
from glob import glob
import pickle


# class Video2frames:
#     def __init__(self, frames_path: str):
#         self.frame_path = frames_path
#
#     def save_frames(self, pic_path, video_path):
#         if os.path.exists(pic_path):
#             print("path of pictures exist\nloading frames...")
#             if len(glob(pic_path + "/*")) > 0:
#                 print("whole frames loaded!")
#                 return glob(pic_path + "/*")
#
#         # Create a VideoCapture object and read from input file
#         video = cv2.VideoCapture(video_path)
#         if not video.isOpened():
#             print("Could not Open :", video_path)
#             exit(0)
#
#         # Prepare directory for saving frames
#         try:
#             if not os.path.exists(pic_path):
#                 print("making path...")
#                 os.makedirs(pic_path)
#         except OSError:
#             print("Error: Creating directory. " + pic_path)
#
#         # Frame extraction
#         count = 0
#         print("start frame extraction...")
#         while video.isOpened():
#             ret, image = video.read()
#             if not ret:
#                 break
#             cv2.imwrite(pic_path + "/frame%d.jpg" % count, image)
#             # print('Saved frame number :', str(int(video.get(1))))
#             count += 1
#         video.release()
#         print("frame totaly extracted!")
#         return glob(pic_path + "/*")
#
#     def picture_reader(self, pic_path, video_path):
#         img_list = self.save_frames(pic_path, video_path)
#         dict4sort = {}
#         print("sorting frames...")
#         for img_path in img_list:
#             frame_num = int(img_path.split("e")[-1].split(".")[0])
#             dict4sort[frame_num] = img_path
#         frames = []
#         for frame_num in sorted(dict4sort):
#             frames.append(cv2.imread(dict4sort[frame_num]))
#         print("frames sorted!")
#         return frames
#
#     def get_1fps(self, left_picpath, right_picpath, left_video_path, right_video_path):
#         if os.path.exists(f"{self.frame_path}/frames_1q_5(10fps).pkl"):
#             print("frame.pkl exists!\nloading frame file...")
#             with open(f"{self.frame_path}/frames_1q_5(10fps).pkl", "rb") as load:
#                 frames = pickle.load(load)
#             print("frame.pkl loaded!")
#             return frames
#         left_frames = self.picture_reader(left_picpath, left_video_path)
#         right_frames = self.picture_reader(right_picpath, right_video_path)
#         right_frames = right_frames[10:]
#         print("generating frame dictionary...")
#         min_frame_len = min(len(left_frames), len(right_frames))
#         fps1_frame_nums = [frame_num for frame_num in range(0, min_frame_len, 3)]
#         left_frames_1fps = [left_frames[i] for i in fps1_frame_nums]
#         right_frames_1fps = [right_frames[i] for i in fps1_frame_nums]
#         frames = {"left": left_frames_1fps, "right": right_frames_1fps}
#         print("dictionary generated!\nsaving dictionary...")
#         with open(f"{self.frame_path}/frames_1q_5(10fps).pkl", "wb") as save:
#             pickle.dump(frames, save)
#         print("dictionary saved!")
#         return frames


class Video2frames:
    def __init__(self, frames_path: str):
        self.frame_path = frames_path

    def save_frames(self, pic_path, video_path):  # 여기서 'svae_frames' 오타 수정
        if os.path.exists(pic_path):
            print("path of pictures exist\nloading frames...")
            if len(glob(pic_path + "/*")) > 0:
                print("whole frames loaded!")
                return glob(pic_path + "/*")

        # Create a VideoCapture object and read from input file
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            print("Could not Open :", video_path)
            exit(0)

        # Prepare directory for saving frames
        try:
            if not os.path.exists(pic_path):
                print("making path...")
                os.makedirs(pic_path)
        except OSError:
            print("Error: Creating directory. " + pic_path)

        # Frame extraction
        count = 0
        print("start frame extraction...")
        while video.isOpened():
            ret, image = video.read()
            if not ret:
                break
            cv2.imwrite(pic_path + "/frame%d.jpg" % count, image)
            count += 1
        video.release()
        print("frame totally extracted!")
        return glob(pic_path + "/*")

    def picture_reader(self, pic_path, video_path):
        img_list = self.save_frames(pic_path, video_path)
        dict4sort = {}
        print("sorting frames...")
        for img_path in img_list:
            frame_num = int(img_path.split("e")[-1].split(".")[0])
            dict4sort[frame_num] = img_path
        frames = []
        for frame_num in sorted(dict4sort):
            frames.append(cv2.imread(dict4sort[frame_num]))
        print("frames sorted!")
        return frames

    def get_1fps(self, left_picpath, right_picpath, left_video_path, right_video_path):
        pkl_path = os.path.join(self.frame_path, "frames_1q_5(10fps).pkl")
        if os.path.exists(pkl_path):
            print("frame.pkl exists!\nloading frame file...")
            with open(pkl_path, "rb") as load:
                frames = pickle.load(load)
            print("frame.pkl loaded!")
            return frames
        left_frames = self.picture_reader(left_picpath, left_video_path)
        right_frames = self.picture_reader(right_picpath, right_video_path)
        right_frames = right_frames[10:]
        print("generating frame dictionary...")
        min_frame_len = min(len(left_frames), len(right_frames))
        fps1_frame_nums = [frame_num for frame_num in range(0, min_frame_len, 3)]
        left_frames_1fps = [left_frames[i] for i in fps1_frame_nums]
        right_frames_1fps = [right_frames[i] for i in fps1_frame_nums]
        frames = {"left": left_frames_1fps, "right": right_frames_1fps}
        print("dictionary generated!\nsaving dictionary...")
        os.makedirs(self.frame_path, exist_ok=True)
        with open(pkl_path, "wb") as save:
            pickle.dump(frames, save)
        print("dictionary saved!")
        return frames
