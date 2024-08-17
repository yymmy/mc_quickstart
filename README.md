## 简介
用于多用户工作环境下的一个启动脚本
1. 修改120帧
2. 复制登录数据（切换用户后无需重新登录）
3. 复制配置文件（画质等）
4. 修改分辨率及全屏


## 使用说明
### 1.修改config.json
config.json内配置用户名以及对应的“配置文件夹”
* copy_source_dir：游戏内的画质等配置所保存的数据文件
* resolution.ResolutionSizeX && resolution.ResolutionSizeY：分辨率，支持哪些查看游戏内来修改
* FullscreenMode：是否全屏，2好像是无边框


### 2.复制“配置的数据库文件”
游戏路径：\Wuthering Waves Game\Client\Saved\LocalStorage
复制此文件夹中的内容，此处需要新建两个文件夹，分别对应了两个用户登录时所需要的配置文件（脚本挂机时一般是低配）


### 3.整体复制到游戏目录内
如图
![image](https://github.com/user-attachments/assets/572922a9-5eed-4301-a68b-f8435634599b)
