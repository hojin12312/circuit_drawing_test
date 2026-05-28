# Circuit Drawing Test (circuit_drawing_test)

Pure Python + SVG 회로도 생성 라이브러리. 넷리스트(SPICE 포맷)를 읽어서 자동으로 스케마틱을 그리고, GitHub Pages로 정적 호스팅한다.

**GitHub**: `hojin12312/circuit_drawing_test` (Public)  
**Pages**: `https://hojin12312.github.io/circuit_drawing_test/`

---

## 프로젝트 구조

| 파일/디렉토리 | 설명 |
|---|---|
| `schematic.py` | 코어 라이브러리 — 회로도 SVG 생성 (무의존성) |
| `inverter.py` | CMOS 인버터 예제 (SVG 생성 스크립트) |
| `build.py` | 로컬 빌드: SVG 재생성 + `index.html`에 커밋 해시 주입 |
| `deploy.sh` | 로컬 배포: 빌드 → 커밋 → 푸시 |
| `index.html` | GitHub Pages 엔트리 페이지 (`__COMMIT_HASH__` 플레이스홀더 포함) |
| `output/inverter.svg` | 생성된 SVG (CI에서 재생성) |
| `.github/workflows/pages.yml` | GitHub Actions — 푸시 시 SVG 생성 + 해시 주입 + Pages 배포 |
| `build.py` | 로컬 빌드 스크립트 (SVG 생성, index.html 해시 업데이트) |

## Architecture

- **`Schematic`** 클래스 — SVG 캔버스, 요소 리스트 관리, SVG 문자열 출력
- **`Element`** 하위 클래스들:
  - `Transistor` — NMOS/PMOS 심볼 (2-vertical-line gate + body, PMOS 버블)
  - `Wire` — 연속 와이어 세그먼트
  - `Junction` — 접합 도트
  - `Label` — 텍스트 라벨
  - `PowerRail` — VDD/GND 전원 레일 + 접지 심볼
- 모든 SVG 생성은 순수 Python 문자열 템플릿 (무의존성)

## 트랜지스터 심볼 규격

- Drain/Source plate: 36px 너비
- Body vertical line: center+2px, 28px 높이
- Gate vertical line: center-10px, 20px 높이 (cap ±4px)
- PMOS 구분: gate 라인 위 흰색 원 (r=5)
- 이름 라벨: `(cx+50, cy+h2+18)` — 트랜지스터 우측 아래

## 현재 지원 회로

- CMOS 인버터 (Phase 1, 수동 배치)
- 넷리스트 → 자동 배치/라우팅: Phase 2 계획

## 개발 / 배포

```bash
# 로컬 빌드
python3 inverter.py    # SVG 생성
python3 build.py       # index.html 해시 업데이트

# 배포 (풀 자동)
bash deploy.sh "커밋 메시지"

# 또는 수동 커밋 후 푸시 (CI가 Pages 배포)
git add -A && git commit -m "..." && git push
```

CI (`pages.yml`)에서 자동 처리:
1. Python으로 `inverter.py` 실행 → SVG 생성
2. `GITHUB_SHA`로 index.html의 `__COMMIT_HASH__` 치환
3. `actions/upload-pages-artifact` + `deploy-pages`로 배포

## Coordinate System

SVG 좌표계 (0,0 = 좌상단). 표준 인버터 레이아웃:

| 요소 | 위치 |
|---|---|
| VDD rail | y=60 |
| PMOS center | (280, 125) |
| Gate poly | x=195, y=125~275 |
| IN wire | y=170 |
| OUT wire | y=210 |
| NMOS center | (280, 275) |
| GND rail | y=360 |
| M2 label | (330, 159) |
| M1 label | (330, 309) |

## 향후 계획 (Phase 2)

- SPICE 넷리스트 파서 (`netlist.py`)
- 자동 배치 엔진 (CMOS 표준 구조 인식)
- 자동 라우팅 (게이트 폴리, 드레인 연결, 전원 레일)
- 추가 소자: 저항(R), 커패시터(C), 다이오드(D)
- 다단 회로 지원
