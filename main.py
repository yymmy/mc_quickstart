import json
import os
import shutil
import sqlite3
import re


def read_config():
    with open('config.json', 'r') as file:
        return json.load(file)


def select_launcher():
    config = read_config()
    base_dir = os.getcwd()
    user_name = os.getlogin()
    user_config = config['users'].get(user_name)

    if not user_config:
        print(f"错误: 找不到用户 {user_name} 的配置信息！")
        return

    # 根据用户名决定文件复制的路径
    user_specific_copy(base_dir, user_config)

    # 修改游戏设置
    modify_game_settings(base_dir, user_config)

    local_storage_path = os.path.join(base_dir, "Client", "Saved", "LocalStorage", "LocalStorage.db")
    if os.path.exists(local_storage_path):
        modify_frame_rate(local_storage_path)
    else:
        print("错误: 找不到文件！")


    # 同步文件夹
    sync_folders(config['users'])

    # 启动 Wuthering Waves.exe
    exe_path = os.path.join(base_dir, "Wuthering Waves.exe")
    if os.path.exists(exe_path):
        os.startfile(exe_path)
    else:
        print("错误: 找不到 Wuthering Waves.exe！")



def user_specific_copy(base_dir, user_config):
    src_dir = os.path.join(base_dir, user_config['copy_source_dir'])
    target_dir = os.path.join(base_dir, "Client", "Saved", "LocalStorage")
    src_files = ["LocalStorage.db", "LocalStorage.db-journal"]

    for file in src_files:
        src_path = os.path.join(src_dir, file)
        target_path = os.path.join(target_dir, file)
        if os.path.exists(src_path):
            shutil.copy(src_path, target_path)
            print(f"文件 {file} 已从 {src_path} 复制到 {target_path}")
        else:
            print(f"错误: 找不到文件 {file}!")


def modify_game_settings(base_dir, user_config):
    config_file_path = os.path.join(base_dir, "Client", "Saved", "Config", "WindowsNoEditor", "GameUserSettings.ini")
    update_config_file(config_file_path, user_config['resolution'])


def update_config_file(config_file_path, new_settings):
    try:
        with open(config_file_path, 'r') as file:
            lines = file.readlines()

        for i in range(len(lines)):
            for key, value in new_settings.items():
                if re.match(f"^{key}=", lines[i]):
                    lines[i] = f"{key}={value}\n"

        with open(config_file_path, 'w') as file:
            file.writelines(lines)
        print("配置文件更新完成。")

    except Exception as e:
        print(f"配置文件更新失败: {str(e)}")


def modify_frame_rate(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM LocalStorage WHERE key = 'GameQualitySetting'")
        result = cursor.fetchone()

        if result:
            settings = json.loads(result[0])
            settings["KeyCustomFrameRate"] = 120
            new_value = json.dumps(settings)
            cursor.execute("UPDATE LocalStorage SET value = ? WHERE key = 'GameQualitySetting'", (new_value,))
            conn.commit()
            print("修改完成: 帧率上限已设置为120")
        else:
            print("错误: 找不到设置项！")

    except Exception as e:
        print(f"数据库错误: {str(e)}")
    finally:
        if conn:
            conn.close()


def sync_folders(users):
    user_names = list(users.keys())
    if len(user_names) != 2:
        print("配置错误: 应当有两个用户。")
        return

    app_data_base = "C:\\Users\\"  # 获取系统的 APPDATA 路径
    source_folder = os.path.join(app_data_base, user_names[0], "AppData", "Roaming", "KR_G152", "A1381")
    target_folder = os.path.join(app_data_base, user_names[1], "AppData", "Roaming", "KR_G152", "A1381")
    sync_folders_logic(source_folder, target_folder)


def sync_folders_logic(source_folder, target_folder):
    source_file = os.path.join(source_folder, "KRSDKUserCache.json")
    target_file = os.path.join(target_folder, "KRSDKUserCache.json")

    # print(f"调试: 源文件路径: {source_file}")
    # print(f"调试: 目标文件路径: {target_file}")

    if not os.path.exists(source_file) and not os.path.exists(target_file):
        print(f"错误: 在两个文件夹中都找不到 KRSDKUserCache.json 文件。")
        return

    if os.path.exists(source_file):
        source_mtime = os.path.getmtime(source_file)
        print(f"调试: 源文件的修改时间: {source_mtime}")
    else:
        source_mtime = 0
        print(f"调试: 源文件不存在，设置源文件修改时间为 0")

    if os.path.exists(target_file):
        target_mtime = os.path.getmtime(target_file)
        print(f"调试: 目标文件的修改时间: {target_mtime}")
    else:
        target_mtime = 0
        print(f"调试: 目标文件不存在，设置目标文件修改时间为 0")

    if source_mtime > target_mtime:
        print(f"调试: 源文件较新，开始从 {source_folder} 同步到 {target_folder}")
        copy_entire_folder(source_folder, target_folder)
        print(f"从 {source_folder} 同步到 {target_folder} 完成。")
    elif target_mtime > source_mtime:
        print(f"调试: 目标文件较新，开始从 {target_folder} 同步到 {source_folder}")
        copy_entire_folder(target_folder, source_folder)
        print(f"从 {target_folder} 同步到 {source_folder} 完成。")
    else:
        print("调试: 两个文件的修改时间相同，无需同步。")


def copy_entire_folder(src_folder, dest_folder):
    # print(f"调试: 开始复制文件夹，从 {src_folder} 到 {dest_folder}")

    if not os.path.exists(dest_folder):
        # print(f"调试: 目标文件夹 {dest_folder} 不存在，创建中...")
        os.makedirs(dest_folder)

    for item in os.listdir(src_folder):
        src_path = os.path.join(src_folder, item)
        dest_path = os.path.join(dest_folder, item)

        if os.path.isdir(src_path):
            # print(f"调试: {src_path} 是文件夹，递归复制...")
            copy_entire_folder(src_path, dest_path)
        else:
            # print(f"调试: 正在复制文件 {src_path} 到 {dest_path}")
            shutil.copy2(src_path, dest_path)
            # print(f"文件 {src_path} 已复制到 {dest_path}")
if __name__ == "__main__":
    try:
        select_launcher()
    except Exception as e:
        print(f"程序运行时发生错误: {str(e)}")
    finally:
        input("按任意键退出...")