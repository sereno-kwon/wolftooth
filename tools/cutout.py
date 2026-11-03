"""흰 배경 제품 컷의 배경을 지워(누끼) 히어로용 투명 WebP로 저장합니다.

사용법: python3 tools/cutout.py dropstop packpliers morse
  images/p/<id>-1.jpg  ->  images/hero/<id>.webp
가장자리에서 이어지는 흰 영역과, 제품 안쪽에 갇힌 넓은 순백 영역(구멍)을 지웁니다. 작은 흰 글씨 등은 남습니다.
필요: pillow, numpy, scipy (pip install pillow numpy scipy)
"""
import sys, pathlib
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parent.parent

def cutout(src, dst, lo=10, hi=34, max_side=1400):
    im = Image.open(src).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    # 흰색에서 얼마나 떨어졌는지 (밝기 + 채도)
    dist = np.maximum(255 - a.min(axis=2), a.max(axis=2) - a.min(axis=2))
    bg = dist < hi
    lab, _ = ndimage.label(bg)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    edge = edge[edge > 0]
    region = np.isin(lab, edge)
    # 제품 안쪽에 갇힌 흰 영역(체인링 구멍 등)도 충분히 크고 순백에 가까우면 배경으로 봅니다
    sizes = ndimage.sum(np.ones_like(dist), lab, index=np.arange(1, lab.max() + 1))
    meds = ndimage.median(dist, lab, index=np.arange(1, lab.max() + 1))
    holes = [i + 1 for i, (n, m) in enumerate(zip(sizes, meds)) if n > dist.size * 0.0004 and m < 3]
    region |= np.isin(lab, holes)
    # 배경 영역 안에서는 흰색에 가까울수록 투명하게 (부드러운 경계, 옅은 그림자 유지)
    alpha = np.ones(dist.shape, np.float32)
    ramp = np.clip((dist - lo) / (hi - lo), 0, 1)
    alpha[region] = ramp[region]
    alpha = ndimage.gaussian_filter(alpha, 0.7)
    # 흰 테두리 번짐 제거: 반투명 픽셀의 색을 흰색에서 분리
    al = np.clip(alpha, 1e-3, 1)[..., None]
    rgb = np.clip((a - 255 * (1 - al)) / al, 0, 255)
    rgba = np.dstack([rgb, alpha * 255]).astype(np.uint8)
    out = Image.fromarray(rgba, 'RGBA')
    out = out.crop(out.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())
    out.thumbnail((max_side, max_side), Image.LANCZOS)
    out.save(dst, 'WEBP', quality=88, method=6)
    return out.size

if __name__ == '__main__':
    for pid in sys.argv[1:]:
        dst = ROOT / f'images/hero/{pid}.webp'
        print(pid, cutout(ROOT / f'images/p/{pid}-1.jpg', dst), dst.stat().st_size // 1024, 'KB')
