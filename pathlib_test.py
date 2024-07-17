from pathlib import WindowsPath

root = WindowsPath(WindowsPath(__file__).parent)
print((type(root)))
story_title = "This story"
story_dir = root/story_title
print(story_dir)