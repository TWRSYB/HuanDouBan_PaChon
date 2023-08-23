import re

values = '1,2,0,3,"1","2","全部",9,"可下载","含短评","发布日期排序","2022-07-30 15:08:29",8,"含字幕","磁链更新排序","有码","无码","欧美","BDSM-077",5,"国产",10,12,"cinema","0","3",6,"4.75GB, 1個文件",null,"all",4,"actor",20,"downable","comment","movie","影片","series","director","number","piece","","magnet:?xt=urn:btih:ce9ecb40545c3f6dd0a82a56e1c0f66b5a110f3f&dn=[HDouban.com]BDSM-077","magnet:?xt=urn:btih:adc601f75774ae4b3784b32495a3b04cd4145d14&dn=[HDouban.com]BDSM-077","_bdsm077","magnet:?xt=urn:btih:635b93ba8675d6b8a3d17973a600909824907d26&dn=[HDouban.com]_bdsm077","3.70GB",7,void 0,"caption","publish","domestic","owncode","codeless","europe","FC2","fc2","演员","系列","film","片商","导演","番号","片单"' +','
findall = re.findall(r'(([^,^"]*?)|("[^"]*?")),', values)
value_list = [x[0].replace('"', '') for x in findall]

keys = 'a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,_,$,aa,ab,ac,ad,ae,af,ag,ah,ai,aj'
key_list = keys.split(',')

if len(value_list) != len(key_list):
    print(len(value_list))
    print(len(key_list))
    print(value_list)
    print(key_list)
    print(1/0)


