# import os
#
# dir_path = r'D:\10.temp\06.黄豆瓣数据爬取\01.TEMP\images\Movie_gallery_pic_studio_fanhao'
#
# for entry in os.scandir(dir_path):
#     print(entry)
#
import os
import shutil


def rename_and_move_folders(directory):
    # 获取目录下的所有文件夹
    folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
    print(f"在当前目录下一共有{len(folders)}个文件夹")
    folders_with_sub_folders = []
    for folder in folders:
        folder_path = os.path.join(directory, folder)
        subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]

        if subfolders:
            folders_with_sub_folders.append(folder)

    print(f"共有{len(folders_with_sub_folders)}个文件夹包含子文件夹")

    for folder in folders_with_sub_folders:
        print(
            "===================================================================================================================")
        folder_path = os.path.join(directory, folder)
        subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]

        print(f"处理文件夹: {folder}")

        if subfolders:
            for subfolder in subfolders:
                new_folder_name = f"{folder}-{subfolder}"
                new_folder_path = os.path.join(directory, new_folder_name)
                subfolder_path = os.path.join(folder_path, subfolder)
                print(f"即将重命名{subfolder_path} 为 {new_folder_path}")

                # 重命名子文件夹
                os.rename(subfolder_path, new_folder_path)

            #     # 剪切子文件夹到与父文件夹同一目录下
            #     shutil.move(new_folder_path, directory)
            #

        if len(os.listdir(folder_path)) == 0:
            print(f"即将删除文件夹: {folder}")
            # 删除父文件夹
            os.rmdir(folder_path)
        else:
            print(f"移出子文件夹后还有子文件: {folder_path}")
            a = 1 / 0


# 调用函数并传入目录路径
directory_path = r'D:\10.temp\06.黄豆瓣数据爬取\10.19_cid2\images\Movie_gallery_pic_studio_fanhao'
rename_and_move_folders(directory_path)
