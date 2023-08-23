import re

script_text = '''
                        big_cove:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/big_cover.jpg",
						trailer:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/trailer.mp4",
						trailer:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/trailer.mp4",
						map:[
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_1.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_1.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_2.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_2.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_3.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_3.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_4.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_4.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_5.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_5.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_6.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_6.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_7.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_7.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_8.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_8.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_9.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_9.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_10.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_10.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_11.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_11.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_12.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_12.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_13.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_13.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_14.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_14.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_15.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_15.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_16.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_16.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_17.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_17.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_18.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_18.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_19.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_19.jpg"},
							{img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_img_20.jpg",big_img:"https://wimg.9618599.com/resources/javdb.com/629761f44b7225302fe1857e/preview_big_img_20.jpg"}
						],
						score:q,
						score_people:106,
						comment_num:c,
						flux_linkage_num:11,
						flux_linkage:[
							{name:"NACR-545-C_X1080X",time:e,url:"magnet:?xt=urn:btih:d63f3832cd75d899005858773fe1ec6e45ed659c&dn=[javdb.com]NACR-545-C_X1080X",meta:"5.25GB, 1個文件","is-small":m,"is-warning":P},
							{name:"nacr-545-C.torrent",time:e,url:"magnet:?xt=urn:btih:a288776939fcbef7cb76180fe66ae59d1bb32d71&dn=[javdb.com]nacr-545-C.torrent",meta:"4.95GB, 1個文件","is-small":m,"is-warning":P},
							{name:F,time:e,url:"magnet:?xt=urn:btih:7aee64e1acac186d0cae588ae633c2b449f561ef&dn=[javdb.com]NACR-545",meta:"5.15GB, 1個文件","is-small":m,"is-warning":d},
							{name:Q,time:e,url:"magnet:?xt=urn:btih:fbdc23777116437399ea2cd58d9b2143a26147a6&dn=[javdb.com]NACR-545-C字幕",meta:"5.52GB","is-small":m,"is-warning":d},
							{name:Q,time:e,url:"magnet:?xt=urn:btih:cc26c3a464bfac2b9c82b11e72b012360063b580&dn=[javdb.com]NACR-545-C字幕",meta:"5.45GB","is-small":m,"is-warning":d},
							{name:"@nacr545",time:e,url:"magnet:?xt=urn:btih:ad29b6158463c12db93a09c93d9b4f1258b01bc6&dn=[javdb.com]@nacr545",meta:"3.86GB","is-small":m,"is-warning":d},
							{name:"NACR-545-FHD",time:e,url:"magnet:?xt=urn:btih:854ca093342b32b31054da12c2258c766c0d14c2&dn=[javdb.com]NACR-545-FHD",meta:"3.20GB","is-small":m,"is-warning":d},
							{name:"HD_NACR-545",time:e,url:"magnet:?xt=urn:btih:10902118c6c0b5590f5b712c03a5878b82d08fa7&dn=[javdb.com]HD_NACR-545",meta:"2.25GB","is-small":d,"is-warning":d},
							{name:F,time:e,url:"magnet:?xt=urn:btih:a2e70007c708544207c1f6319c9ae247d6c7e8ff&dn=[javdb.com]NACR-545",meta:"1.85GB","is-small":d,"is-warning":d},
							{name:"NACR-545C.mp4 ",time:e,url:"magnet:?xt=urn:btih:a4e3103114107a10b67d0009c8d367162c315726&dn=[javdb.com]NACR-545C.mp4 ",meta:"1.70GB","is-small":d,"is-warning":d},
							{name:"NACR-545C ",time:e,url:"magnet:?xt=urn:btih:cb27d4d7254d70abcdd6b9dfe3347c4edc01c42b&dn=[javdb.com]NACR-545C ",meta:"1.26GB","is-small":d,"is-warning":d}
						],'''

search = re.search(r'trailer:"(.+?.mp4)",', script_text)
if search:
    print(search.group(1).replace(r'\u002F', '/'))
    groups = search.groups()
    print(len(groups))
    if len(groups) != 1:
        a = 1 / 0