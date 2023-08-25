import re
# url = 'https://wimg.9618599.com/resources/javbus.com/631f81bd95304ec4c6a63edf/big_cover.jpg?84'
# match_invalid_subfix = re.match(r'(.+\.jpg)\?\d+$', url)
# if match_invalid_subfix:
#     print(f"发现了url以jpg?xx结尾的情况: url: {url}")
#     url = match_invalid_subfix.group(1)
#     print(f"新的url为: {url}")
from Config.Config import PIC_DIR_MOVIE_GALLERY_PIC_STUDIO_FANHAO

chars_cant_in_filename = r'[\\/:"*?<>|]+'
dir_studio_fanhao = f"{PIC_DIR_MOVIE_GALLERY_PIC_STUDIO_FANHAO}" \
                    f"/{re.sub(chars_cant_in_filename, '-', '一本道*起飞')}" \
                    f"_番号"

print(dir_studio_fanhao)