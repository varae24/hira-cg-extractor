"""生成离线 index.html 画廊。

单文件、无外部依赖：深色主题、分组筛选、搜索、点击看原图、视频单独播放。
所有图片/视频都通过相对路径引用，便于整目录打包带走。
"""

import json
import time

_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#0e1013;--panel:#16191f;--line:#252a33;--fg:#e8ebf0;--dim:#8b93a1;--ac:#7cc4ff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
 font:14px/1.6 "Segoe UI","Microsoft YaHei",system-ui,sans-serif}
header{position:sticky;top:0;z-index:10;background:rgba(14,16,19,.94);
 backdrop-filter:blur(10px);border-bottom:1px solid var(--line);padding:16px 22px}
h1{margin:0 0 4px;font-size:19px;font-weight:600;letter-spacing:.5px}
.sub{color:var(--dim);font-size:12px}
.bar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:12px}
input[type=search]{flex:1;min-width:200px;padding:8px 12px;border-radius:8px;
 border:1px solid var(--line);background:var(--panel);color:var(--fg);font-size:13px}
input[type=search]:focus{outline:none;border-color:var(--ac)}
.chip{padding:6px 13px;border-radius:999px;border:1px solid var(--line);
 background:var(--panel);color:var(--dim);cursor:pointer;font-size:12px;user-select:none}
.chip:hover{border-color:var(--ac);color:var(--fg)}
.chip.on{background:var(--ac);border-color:var(--ac);color:#08121c;font-weight:600}
main{padding:20px 22px 60px}
.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;
 overflow:hidden;cursor:pointer;transition:.15s}
.card:hover{border-color:var(--ac);transform:translateY(-2px)}
.card img{width:100%;height:150px;object-fit:cover;display:block;background:#000}
.card .m{padding:8px 10px;font-size:12px}
.card .n{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.card .d{color:var(--dim);font-size:11px;margin-top:2px}
.vid{position:relative}
.vid::after{content:"\25B6";position:absolute;inset:0;display:flex;align-items:center;
 justify-content:center;font-size:34px;color:#fff;text-shadow:0 2px 12px #000;opacity:.85}
.vid:hover::after{opacity:1}
h2{font-size:15px;margin:26px 0 12px;padding-left:9px;
 border-left:3px solid var(--ac);font-weight:600}
h2 small{color:var(--dim);font-weight:400;margin-left:8px;font-size:12px}
#lb{position:fixed;inset:0;background:rgba(0,0,0,.93);display:none;
 align-items:center;justify-content:center;z-index:99;cursor:zoom-out}
#lb.on{display:flex}
#lb img{max-width:96vw;max-height:96vh;object-fit:contain}
#x{position:fixed;top:16px;right:22px;color:#fff;font-size:30px;cursor:pointer;opacity:.7}
.empty{color:var(--dim);padding:60px 0;text-align:center}
</style></head><body>
<header>
  <h1>__TITLE__</h1>
  <div class="sub">__COUNT__ 项 &middot; __SIZE__ &middot; 生成于 __DATE__ &middot; 素材版权归原厂所有，仅供个人留存</div>
  <div class="bar">
    <input type="search" id="q" placeholder="搜索文件名，例如 ev002 / bg01 / Atlas...">
    <span class="chip on" data-g="*">全部</span>
    __CHIPS__
  </div>
</header>
<main id="main"></main>
<div id="lb"><span id="x">&times;</span><img id="lbimg" alt=""></div>
<script>
const DATA=__DATA__;
let cur='*',q='';
const main=document.getElementById('main');
function nat(s){const m=s.match(/^([A-Za-z_]*)(\d*)(.*)$/);
  return m&&m[2]?[m[1],+m[2],m[3]]:['~',0,s];}
function render(){
  main.innerHTML='';
  const kw=q.trim().toLowerCase();
  const list=DATA.filter(d=>(cur==='*'||d.g===cur)&&(!kw||d.n.toLowerCase().includes(kw)))
    .sort((a,b)=>{const x=nat(a.n),y=nat(b.n);
      return x[0]<y[0]?-1:x[0]>y[0]?1:x[1]-y[1]||(x[2]<y[2]?-1:1);});
  if(!list.length){main.innerHTML='<div class="empty">没有匹配的资源</div>';return;}
  const gs=[...new Set(list.map(d=>d.g))].sort();
  for(const g of gs){
    const items=list.filter(d=>d.g===g);
    const h=document.createElement('h2');
    h.innerHTML=g+' <small>'+items.length+'</small>';
    main.appendChild(h);
    const gr=document.createElement('div');gr.className='grid';
    for(const d of items){
      const c=document.createElement('div');
      c.className='card'+(d.v?' vid':'');
      const meta=d.v?(d.d+' 秒 &middot; '+d.mb+' MB'):
        ('&times;'+d.w+'<span style="opacity:.5"> &middot; </span>'+d.mb+' MB');
      const thumb=d.t?('<img loading="lazy" src="'+d.t+'" alt="'+d.n+'">'):'';
      c.innerHTML=thumb+'<div class="m"><div class="n">'+d.n+'</div>'+
        '<div class="d">'+meta+'</div></div>';
      c.onclick=()=>{ if(d.v){window.open(d.f,'_blank');return;}
        document.getElementById('lbimg').src=d.f;
        document.getElementById('lb').classList.add('on');};
      gr.appendChild(c);
    }
    main.appendChild(gr);
  }
}
document.getElementById('q').oninput=e=>{q=e.target.value;render();};
document.querySelectorAll('.chip').forEach(c=>c.onclick=()=>{
  document.querySelectorAll('.chip').forEach(x=>x.classList.remove('on'));
  c.classList.add('on');cur=c.dataset.g;render();});
document.getElementById('lb').onclick=()=>document.getElementById('lb').classList.remove('on');
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.getElementById('lb').classList.remove('on');});
render();
</script></body></html>"""


def build_gallery(out_dir, images, videos, title="Unity 资源画廊"):
    """生成 index.html + manifest.json。

    images/videos 为 images.export_all / videos.export_videos 返回的 record 列表。
    """
    data = []
    for d in images:
        data.append({"n": d["name"], "f": d["rel"], "t": d.get("thumb", d["rel"]),
                     "g": d.get("group", "未分类"), "w": d.get("w", 0), "h": d.get("h", 0),
                     "mb": round(d.get("bytes", 0) / 1e6, 2), "v": False})
    for d in videos:
        data.append({"n": d["name"], "f": d["rel"], "t": "", "g": "视频",
                     "w": d.get("w", 0), "h": d.get("h", 0),
                     "mb": round(d.get("bytes", 0) / 1e6, 2),
                     "v": True, "d": d.get("dur", 0)})

    total = sum(d.get("bytes", 0) for d in images) + sum(d.get("bytes", 0) for d in videos)
    chips = "".join('<span class="chip" data-g="%s">%s</span>' % (g, g)
                    for g in sorted({d["g"] for d in data}))
    html = (_TEMPLATE
            .replace("__TITLE__", title)
            .replace("__DATA__", json.dumps(data, ensure_ascii=False))
            .replace("__CHIPS__", chips)
            .replace("__COUNT__", str(len(data)))
            .replace("__SIZE__", "%.1f MB" % (total / 1e6))
            .replace("__DATE__", time.strftime("%Y-%m-%d %H:%M")))

    index_path = out_dir + "/index.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    with open(out_dir + "/manifest.json", "w", encoding="utf-8") as f:
        json.dump({"images": images, "videos": videos}, f, ensure_ascii=False, indent=1)
    return index_path, len(data), total