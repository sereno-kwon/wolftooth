# Wolf Tooth Korea

wolftooth.rubiworkshop.com 원페이지 정적 사이트 (GitHub Pages). quoc.rubiworkshop.com과 같은 구조, 같은 디자인 체계(rubi.kr 2026-10 리디자인)입니다.

- `index.html` 한국어 원페이지 (WOLF TOOTH · RANGE · DRIVETRAIN · COCKPIT · TOOLS · MOUNTS · WHEELS · COLORS · FIT · STORY · SHOWROOM). 빌드 결과물이므로 직접 수정하지 않습니다.
- `index.src.html` 편집용 원본. `{{CARDS:...}}`, `{{RANGE}}` 자리는 빌드 때 `tools/build.py`의 `PRODUCTS` 데이터로 채워집니다.
- `tools/_base.css`, `tools/_base.js` QUOC 코리아 사이트와 같은 공통 스타일·스크립트. `tools/site.css`, `tools/site.js` 울프투스 전용 추가분.
- `tools/build.py` index.html, `.github/image-manifest.txt`, sitemap.xml 생성 (표준 라이브러리만 사용)
- `404.html` 하위 주소(/tools, /pack-pliers, /dropper, /hubs, /dealers 등)를 섹션으로 연결
- `images/p/` 제품 컷(`<제품id>-1.jpg`, `-2.jpg`), `images/life/` 히어로·브랜드 사진(선택)

## 처음 올릴 때
1. 저장소 `sereno-kwon/wolftooth`를 만들고 이 폴더를 main에 푸시합니다.
2. Settings → Pages → Source: Deploy from a branch, Branch: main / (root).
3. 도메인 DNS에 `wolftooth` CNAME 레코드를 `sereno-kwon.github.io`로 추가하고, Pages 설정에서 Custom domain에 `wolftooth.rubiworkshop.com`을 넣은 뒤 Enforce HTTPS를 켭니다 (CNAME 파일은 이미 들어 있음).
4. 푸시하면 `fetch-images.yml`이 울프투스 공식 스토어에서 제품 이미지를 받아 `images/`에 커밋합니다. Actions → Fetch images from Wolf Tooth store 로그에서 `검색어 -> handle` 줄로 어떤 제품이 잡혔는지 확인하고, FAIL이나 엉뚱한 제품이 있으면 매니페스트를 고칩니다.
5. 파비콘은 별도로 넣어야 합니다: `images/favicon-48.png`, `images/favicon-96.png`, `images/apple-touch-icon.png`(180px). 헤더 로고는 지금 텍스트 워드마크입니다.

## 이미지
- 매니페스트 한 줄 형식: `<검색어 | handle:제품주소 | https://이미지주소> <이미지 번호(0부터)> <저장 경로>`
  - 검색어(띄어쓰기는 `+`)로 공식 스토어를 검색해 첫 번째 제품을 씁니다. 다른 제품이 잡히면 `handle:pack-pliers`처럼 제품 주소 끝부분을 적습니다.
  - 매니페스트는 `tools/build.py`가 다시 쓰므로, 검색어는 `PRODUCTS`의 `q`에서 고치고 빌드합니다. 직접 이미지 주소를 넣을 때는 build.py의 `manifest()` 아래쪽 life 줄을 고칩니다.
- 이미 받은 파일은 건너뜁니다. 교체할 때는 파일을 지우거나 같은 경로에 덮어씁니다 (루비 촬영본으로 교체 가능).
- 이미지가 없으면 제품 카드는 제품명 자리표시가 나오고, `images/life/` 사진 자리(.opt)는 페이지에서 숨겨집니다.

## 문구 수정
1. 섹션 문구는 `index.src.html`, 제품 카드·라인업 문구는 `tools/build.py`의 `PRODUCTS`에서 고칩니다.
2. `python3 tools/build.py` 를 실행합니다.

## 링크
- 헤더 SHOP, 각 제품의 "루비워크샵에서 보기": `https://rubiworkshop.com/wolftooth`
- 거래처 문의: 루비서플라이 02-516-8465, 카카오톡 채널 `https://pf.kakao.com/_NFnBj/chat`
- 푸터 INSTAGRAM: `https://www.instagram.com/wolftoothcomponents` (울프투스 글로벌 계정)
