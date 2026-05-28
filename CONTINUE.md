# Continue — Circuit Drawing Test

## Goal

SPICE 넷리스트(또는 유사 포맷)를 입력받아 자동으로 스케마틱(SVG)을 그려주는 Python 스크립트. GitHub Pages로 정적 호스팅.

## Current State (Phase 1 완료)

### Done
- `schematic.py` — 순수 Python + SVG 회로도 라이브러리 (Transistor, Wire, Label, Junction, PowerRail)
- `inverter.py` — CMOS 인버터 수동 배치 예제
- `index.html` — GitHub Pages 엔트리 (CI에서 `GITHUB_SHA`로 해시 자동 주입)
- `build.py` — 로컬 빌드 스크립트
- `deploy.sh` — 로컬 배포 스크립트
- `.github/workflows/pages.yml` — CI: 푸시 시 SVG 생성 + 해시 주입 + Pages 배포
- GitHub Pages 라이브 (`hojin12312.github.io/circuit_drawing_test/`)

### 해결된 이슈
- ✅ 게이트 폴리(세로선) 불필요한 연장 수정 — PMOS 게이트(y=125)에서 NMOS 게이트(y=275)까지만
- ✅ PMOS 버블 위치 — gate 라인 위(r=5, fill=white)로 정정
- ✅ M1/M2 라벨 선 겹침 — `(330, 159)/(330, 309)`로 이동 (트랜지스터 우측 아래)
- ✅ 커밋 해시 표시 — `GITHUB_SHA`로 Pages 푸터에 정확한 해시 표시

### 미해결 / 미구현

1. **SPICE 넷리스트 파서** (`netlist.py`) — 아직 미구현
   - 넷리스트를 읽어서 회로 구조(토폴로지)를 파이썬 객체로 변환
   - 포맷: `M<이름> <type> <드레인> <게이트> <소스>` 또는 표준 SPICE

2. **자동 배치 엔진** — 아직 미구현
   - CMOS 표준 구조 인식 (PMOS 위, NMOS 아래, 공통 게이트)
   - 좌표 자동 계산 및 할당

3. **자동 라우팅** — 아직 미구현
   - 게이트 폴리, 드레인 연결, VDD/GND, 입출력 자동 연결

4. **추가 소자** — R, C, D, 공통 게이트 등 심볼 필요

### Changed Files

- `schematic.py` — 핵심 라이브러리 (329 lines)
- `inverter.py` — 인버터 예제 (83 lines)
- `build.py` — 로컬 빌드 (44 lines)
- `deploy.sh` — 로컬 배포 (43 lines)
- `index.html` — Pages 엔트리 (56 lines)
- `.github/workflows/pages.yml` — CI 워크플로우 (42 lines)
- `CLAUDE.md` — 프로젝트 문서 (new)
- `CONTINUE.md` — 세션 인계 문서 (this file)

### Commit Status

마지막 commit: `33a80cb` — "Fix label overlap: move to (cx+50, cy+h2+18) below and right"  
모든 변경사항 커밋 및 푸시 완료. Working tree clean.

## Next Steps (Phase 2)

1. **`netlist.py`** — SPICE 넷리스트 파서 구현
   - `M1 out in gnd 0 nmos` → Python 객체
   - 트랜지스터, 전원, 입출력 포트 추출
   
2. **자동 배치**
   - CMOS 인버터: VDD(y=60) → PMOS(y=125) → OUT(y=210) → NMOS(y=275) → GND(y=360) 자동 적층
   - 게이트 폴리 자동 배치 (x=공통게이트_x)
   
3. **자동 라우팅**
   - VDD/PMOS/NMOS/GND 세로 연결선
   - 게이트 폴리 가로 연결선
   - IN/OUT 입출력 신호선
   
4. **검증**: `nand.py` 등 추가 예제로 확장성 검증
