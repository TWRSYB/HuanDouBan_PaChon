import os


def rename_and_move_folders(directory):
    # 获取目录下的所有文件夹
    folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
    print(f"在当前目录下一共有{len(folders)}个文件夹")
    folders_with_out_sub_folders = []
    for folder in folders:
        folder_path = os.path.join(directory, folder)
        subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]

        if not subfolders:
            folders_with_out_sub_folders.append(folder)

    print(f"共有{len(folders_with_out_sub_folders)}个文件夹包不含子文件夹")
    print(folders_with_out_sub_folders)

    for folder in folders_with_out_sub_folders:
        print(
            "===================================================================================================================")

        if folder != '_NoStudio':
            print(f"处理文件夹: {folder}")
            folder_path = os.path.join(directory, folder)
            new_folder_path = os.path.join(f"{directory}/_NoStudio", folder)
            print(f"即将重命名{folder_path} 为 {new_folder_path}")

            # 重命名文件夹
            os.rename(folder_path, new_folder_path)


# 调用函数并传入目录路径
directory_path = r'D:\34.Temp\06.黄豆瓣数据爬取\01.TEMP_wait\images\Movie_gallery_pic_studio_fanhao'
rename_and_move_folders(directory_path)
