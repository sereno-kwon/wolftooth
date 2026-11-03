"""Wolf Tooth 코리아 사이트 빌드.

index.src.html(한국어 원본)의 자리표시자를 채워 index.html을 만들고,
.github/image-manifest.txt 와 sitemap.xml 을 다시 씁니다.

  {{CSS}} {{JS}}          tools/_base.css, tools/_base.js (quoc.rubiworkshop.com과 같은 디자인 체계) + tools/site.css
  {{CARDS:a,b,c}}         아래 PRODUCTS의 제품 카드
  {{RANGE}}               라인업 리스트
  {{LD_PRODUCTS}}         JSON-LD Product 노드

사용법: python3 tools/build.py   (표준 라이브러리만 사용)
"""
import json, re, pathlib, datetime, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://wolftooth.rubiworkshop.com/'
SHOP = 'https://rubiworkshop.com/wolftooth'

# ---------------------------------------------------------------- products
# q: 울프투스 공식 스토어 검색어. GitHub Actions가 이 검색어로 제품을 찾아 이미지를 내려받습니다.
#    (검색 결과가 엉뚱하면 q를 공식 사이트의 제품 주소 끝부분(handle)으로 바꾸면 됩니다: 예) handle:pack-pliers)
# img: 받아올 이미지 번호(0부터). 첫 장은 보통 흰 배경의 제품 컷입니다.
PRODUCTS = [
 # Drivetrain
 dict(id='dropstop', name='Drop-Stop Chainrings', ko='드롭스톱 체인링', cat='Drivetrain', q='Drop-Stop chainring', img=[0, 1],
      desc='울프투스의 시작. 넓고 좁은 톱니가 번갈아 체인을 붙잡아, 체인 가이드 없이도 1x 구동계에서 체인이 빠지지 않습니다.',
      spec=[('MOUNT', 'Direct · BCD'), ('SHAPE', 'Round · Oval'), ('MATERIAL', 'Aluminum')]),
 dict(id='goatlink', name='GoatLink · RoadLink', ko='고트링크 · 로드링크', cat='Drivetrain', q='RoadLink', img=[0, 1],
      desc='뒤 디레일러의 위치를 바꿔 더 큰 스프라킷의 카세트를 쓸 수 있게 해주는 링크. 산악은 고트링크, 로드와 그래블은 로드링크.',
      spec=[('USE', 'MTB · Road · Gravel'), ('FOR', 'Wide-range cassette')]),
 dict(id='tanpan', name='Tanpan', ko='탄판', cat='Drivetrain', q='Tanpan', img=[0, 1],
      desc='시마노 로드 변속 레버로 시마노 MTB 디레일러를 쓸 수 있게 케이블 당김 비율을 바꿔주는 작은 어댑터. 드롭바 그래블 세팅의 단골 부품입니다.',
      spec=[('USE', 'Drop bar · MTB derailleur'), ('TYPE', 'Pull ratio adapter')]),
 # Cockpit & Dropper
 dict(id='remote', name='ReMote Dropper Levers', ko='리모트 드로퍼 레버', cat='Cockpit', q='ReMote Pro', img=[0, 1],
      desc='엄지가 자연스럽게 닿는 위치에서 가볍게 눌리는 드로퍼 레버. 바 클램프, 매치메이커, I-Spec 등 다양한 마운트로 나옵니다.',
      spec=[('MOUNT', '22.2 · MatchMaker · I-Spec'), ('ACTION', 'Cable')]),
 dict(id='resolve', name='Resolve Dropper Post', ko='리졸브 드로퍼 포스트', cat='Cockpit', q='Resolve dropper', img=[0, 1],
      desc='라이더가 직접 관리할 수 있도록 설계한 드로퍼 포스트. 트래블 조절과 간단한 정비를 공구 몇 개로 해결합니다.',
      spec=[('TYPE', 'Cable actuated'), ('TRAVEL', 'Adjustable')]),
 dict(id='grips', name='Grips', ko='그립', cat='Cockpit', q='Fat Paw grips', img=[0, 1],
      desc='두툼한 쿠션의 팻 파우, 손바닥 결을 살린 카브, 얇고 정확한 에코. 손과 라이딩에 맞춰 고르는 락온 그립.',
      spec=[('TYPE', 'Lock-on'), ('LINE', 'Fat Paw · Karv · Echo')]),
 dict(id='headset', name='Headsets · Spacers', ko='헤드셋 · 스페이서', cat='Cockpit', q='headset', img=[0, 1],
      desc='정밀 가공한 헤드셋과 스템 스페이서. 울프투스의 아노다이징 컬러로 콕핏에 포인트를 줍니다.',
      spec=[('STANDARD', 'S.H.I.S.'), ('COLOR', 'Anodized')]),
 # Tools
 dict(id='packpliers', name='Pack Pliers', ko='팩 플라이어', cat='Tools', q='Pack Pliers', img=[0, 1],
      desc='체인 마스터 링크 플라이어에 타이어 레버와 밸브 코어 툴을 더하고, 여분의 마스터 링크까지 품은 휴대용 공구.',
      spec=[('FUNCTION', 'Master link · Tire lever · Valve core'), ('USE', 'Trail · Saddle bag')]),
 dict(id='8bit', name='8-Bit Tool System', ko='8비트 툴 시스템', cat='Tools', q='8-Bit', img=[0, 1],
      desc='필요한 공구만 골라 조립하는 모듈형 멀티툴. 집에서는 정비 공구로, 라이딩에서는 휴대 공구로 나눠 씁니다.',
      spec=[('TYPE', 'Modular multi-tool'), ('USE', 'Workshop · Trail')]),
 dict(id='encase', name='EnCase System', ko='인케이스 시스템', cat='Tools', q='EnCase', img=[0, 1],
      desc='핸들바 끝 속에 공구를 숨기는 시스템. 멀티툴과 체인 공구, 타이어 플러그를 늘 자전거에 싣고 다닙니다.',
      spec=[('MOUNT', 'Inside handlebar'), ('USE', 'Always-on-bike tools')]),
 # Cages & Mounts
 dict(id='morse', name='Morse Cage', ko='모스 케이지', cat='Cages & Mounts', q='Morse water bottle cage', img=[0, 1],
      desc='슬롯 마운트로 케이지를 위아래로 옮길 수 있는 물병 케이지. 작은 프레임과 프레임 백 아래에서도 물병을 쉽게 뺍니다.',
      spec=[('MOUNT', 'Slotted · Adjustable'), ('MATERIAL', 'Aluminum')]),
 dict(id='brad', name='B-RAD System', ko='비래드 시스템', cat='Cages & Mounts', q='B-RAD', img=[0, 1],
      desc='물병 보스를 옮기고, 늘리고, 더하는 마운팅 시스템. 펌프와 튜브, 공구, 두 번째 물병까지 원하는 자리에 답니다.',
      spec=[('TYPE', 'Mounting system'), ('USE', 'Bottles · Tools · Gear')]),
 # Wheels & Pedals
 dict(id='hydra', name='Hydra Hubs', ko='하이드라 허브', cat='Wheels & Pedals', q='Hydra hub', img=[0, 1],
      desc='페달을 밟는 즉시 물리는 빠른 인게이지먼트의 허브. 정밀 가공한 셸과 컬러로 휠 빌드의 중심이 됩니다.',
      spec=[('TYPE', 'Rear · Front hub'), ('ENGAGEMENT', 'Fast')]),
 dict(id='waveform', name='Waveform Pedals', ko='웨이브폼 페달', cat='Wheels & Pedals', q='Waveform pedal', img=[0, 1],
      desc='발을 받쳐주는 오목한 플랫폼과 교체형 핀의 플랫 페달. 트레일에서 신발이 페달 위에 단단히 머뭅니다.',
      spec=[('TYPE', 'Flat pedal'), ('PINS', 'Replaceable')]),
 dict(id='valve', name='Tubeless Valve Stems', ko='튜브리스 밸브', cat='Wheels & Pedals', q='valve stems', img=[0, 1],
      desc='막힘 없이 공기를 넣고, 실런트가 굳어도 관리하기 쉬운 튜브리스 밸브. 아노다이징 컬러의 밸브 캡까지.',
      spec=[('TYPE', 'Presta tubeless'), ('COLOR', 'Anodized')]),
]
P = {p['id']: p for p in PRODUCTS}

def esc(s):
    return html.escape(s, quote=True)

def img_path(pid, n):
    return f'images/p/{pid}-{n + 1}.jpg'

def card(pid, i):
    p = P[pid]
    dl = ''.join(f'<dt>{k}</dt><dd>{esc(v)}</dd>' for k, v in p['spec'])
    return (f'<article class="cell reveal"><span class="idx">{i:02d} · {esc(p["cat"])}</span>'
            f'<figure class="pd" data-gallery="{pid}"><img src="{img_path(pid, 0)}" alt="Wolf Tooth {esc(p["name"])}" loading="lazy"></figure>'
            f'<h3><small>{esc(p["ko"])}</small>{esc(p["name"])}</h3><p>{esc(p["desc"])}</p><dl>{dl}</dl>'
            f'<a class="link" href="{SHOP}" target="_blank" rel="noopener"><span>루비워크샵에서 보기</span><svg aria-hidden="true"><use href="#i-arrow"/></svg></a></article>')

def cards(ids):
    ids = [x.strip() for x in ids.split(',')]
    return ''.join(card(x, i + 1) for i, x in enumerate(ids))

SEC = {'Drivetrain': 'drivetrain', 'Cockpit': 'cockpit', 'Tools': 'tools', 'Cages & Mounts': 'mounts', 'Wheels & Pedals': 'wheels'}

def range_list():
    out = []
    for i, p in enumerate(PRODUCTS, 1):
        out.append(f'<a href="#{SEC[p["cat"]]}"><span class="idx">{i:02d}</span><div><b>{esc(p["name"])}</b><small>{esc(p["cat"])}</small></div>'
                   f'<p>{esc(p["desc"].split(". ")[0].rstrip(".") + ".")}</p><dl><dd>{esc(p["ko"])}</dd></dl><svg><use href="#i-arrow"/></svg></a>')
    return '\n      '.join(out)

def ld_products():
    return ',\n    '.join(json.dumps({'@type': 'Product', 'name': 'Wolf Tooth ' + p['name'], 'brand': {'@type': 'Brand', 'name': 'Wolf Tooth Components'},
                                   'category': p['cat'], 'image': SITE + img_path(p['id'], 0), 'description': p['desc']}, ensure_ascii=False)
                        for p in PRODUCTS)

def manifest():
    lines = ['# <검색어 또는 handle:제품주소 또는 https://이미지주소> <이미지 번호> <저장 경로>',
             '# fetch-images.yml이 울프투스 공식 스토어에서 이미지를 받아 images/에 커밋합니다. 이미 받은 파일은 건너뜁니다.']
    for p in PRODUCTS:
        for n in p['img']:
            lines.append(f'{p["q"].replace(" ", "+")} {n} {img_path(p["id"], n)}')
    lines.append('# 히어로 · 브랜드 사진 (라이프스타일 컷). 직접 촬영본이나 공식 이미지 주소로 바꾸세요. 없으면 해당 사진은 페이지에서 숨겨집니다.')
    for n in range(1, 5):
        lines.append(f'# https://example.com/photo-{n}.jpg 0 images/life/0{n}.jpg')
    (ROOT / '.github/image-manifest.txt').write_text('\n'.join(lines) + '\n')

def build():
    s = (ROOT / 'index.src.html').read_text()
    css = (ROOT / 'tools/_base.css').read_text() + '\n/* ===== Wolf Tooth 추가 ===== */\n' + (ROOT / 'tools/site.css').read_text()
    s = s.replace('{{CSS}}', css).replace('{{JS}}', (ROOT / 'tools/_base.js').read_text() + (ROOT / 'tools/site.js').read_text())
    s = re.sub(r'\{\{CARDS:([^}]+)\}\}', lambda m: cards(m.group(1)), s)
    s = s.replace('{{RANGE}}', range_list()).replace('{{LD_PRODUCTS}}', ld_products())
    assert '{{' not in s, re.findall(r'\{\{[^}]*\}\}', s)
    assert '—' not in re.sub(r'<!--.*?-->', '', s, flags=re.S), 'em dash in Korean page'
    (ROOT / 'index.html').write_text(s)
    return s

def sitemap(html_):
    imgs = sorted(set(re.findall(r'images/p/[\w.-]+\.jpg', html_)))
    today = datetime.date.today().isoformat()
    x = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
         'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
         f'  <url>\n    <loc>{SITE}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>1.0</priority>'
         + ''.join(f'\n    <image:image><image:loc>{SITE}{i}</image:loc></image:image>' for i in imgs)
         + '\n  </url>\n</urlset>\n')
    (ROOT / 'sitemap.xml').write_text(x)

if __name__ == '__main__':
    out = build()
    manifest()
    sitemap(out)
    print('index.html', len(out), 'bytes,', len(PRODUCTS), 'products')
