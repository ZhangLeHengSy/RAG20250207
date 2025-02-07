import subprocess

def git_commit_and_push(commit_message, branch='main'):
    try:
        # 添加所有修改和未跟踪的文件
        subprocess.run(['git', 'add', '.'], check=True)
        print("文件已添加到暂存区")
        
        # 提交更改
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        print("提交成功")
        
        # 推送更改到远程仓库
        subprocess.run(['git', 'push', 'origin', branch], check=True)
        print("推送成功")
    except subprocess.CalledProcessError as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    commit_message = "继续提交代码"
    git_commit_and_push(commit_message)