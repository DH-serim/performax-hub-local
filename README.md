# Performax Hub

마케터를 위한 내부 배포용 마케팅 분석 플랫폼.
Python Flask 기반 로컬 서버로 실행되며, PyInstaller로 EXE 패키징 가능.

---

## 기능

### 키워드 트렌드 분석
- 네이버 데이터랩 API 연동
- 키워드 모드 / 그룹 모드 탭 전환
- 쉼표, 탭, 줄바꿈 동시 입력 (엑셀 붙여넣기 지원)
- 그룹 모드: 그룹당 최대 20개 키워드, 최대 5그룹
- 결과: 라인 차트 + 데이터 테이블 + CSV/엑셀 다운로드
- 최근 검색 히스토리 (SQLite, 최근 20개)

### 키워드 쿼리 조회
- 네이버 검색광고 API RelKwdStat 연동
- 최대 100개 키워드 입력 (5개씩 분할 호출)
- 연관 키워드 포함/미포함 선택
- 결과: PC/모바일 월검색수, 총검색수, 클릭수, 클릭률, 경쟁정도
- CSV/엑셀 다운로드
- 최근 검색 히스토리 (SQLite, 최근 20개)

### UTM 빌더
- 구글 시트 기반 UTM 규칙 관리
- 광고주별 UTM 파라미터 구성 (매체, 광고유형, 캠페인명, 타겟팅, 상품)
- utm_term 자동 조합 (시작일_디바이스_연령_성별_타겟팅_최적화_소재명)
- 타겟팅 규칙 팝업 가이드
- 결과 엑셀 다운로드

---

## 설치 및 실행

### 요구사항
- Python 3.9 이상
- 패키지: `flask`, `requests`

### 패키지 설치
```bash
pip install flask requests
```

### API 키 설정
`app.py` 상단에 API 키를 입력하세요.

```python
# 네이버 데이터랩
NAVER_CLIENT_ID     = "여기에_Client_ID_입력"
NAVER_CLIENT_SECRET = "여기에_Client_Secret_입력"

# 네이버 검색광고
SEARCHAD_API_KEY     = "여기에_API_KEY_입력"
SEARCHAD_SECRET_KEY  = "여기에_SECRET_KEY_입력"
SEARCHAD_CUSTOMER_ID = "여기에_CUSTOMER_ID_입력"
```

### 실행
```bash
python app.py
```
실행하면 브라우저가 자동으로 열립니다. (`http://localhost:5000`)

---

## EXE 빌더 패키징

```bash
build.bat
```

`dist/PerformaxHub.exe` 생성. 더블클릭으로 실행 가능.

---

## UTM 빌더 구글 시트 설정

UTM 빌더는 구글 시트를 통해 광고주별 UTM 규칙을 관리합니다.

### 구글 시트 구조 (4개 시트)

| 시트명 | 설명 |
|---|---|
| `CLIENT_MASTER` | 광고주 기본 정보 |
| `UTM_PARAM_CONFIG` | 광고주별 UTM 파라미터 구성 |
| `UTM_CODE_MASTER` | 드롭다운 선택값 및 입력 타입 |
| `UTM_COMBINE_RULE` | utm_term 조합 순서/구분자 |
| `UTM_GUIDE` | 타겟팅 등 규칙 가이드 |

### 구글 시트 공유 설정
1. 구글 시트 우측 상단 **공유** 클릭
2. **링크가 있는 모든 사용자** 선택
3. 권한: **뷰어**
4. UTM 빌더에서 URL 입력 후 **불러오기**

### UTM_PARAM_CONFIG 입력방식
| 값 | 설명 |
|---|---|
| `text` | 직접 입력 |
| `select` | 드롭다운 선택 (UTM_CODE_MASTER 참조) |
| `date` | 날짜 선택 → YYMMDD 자동 변환 |
| `combine` | 조합형 (UTM_COMBINE_RULE 참조) |

---

## 데이터 저장

히스토리 및 설정은 로컬 SQLite DB에 저장됩니다.
- 경로: `~/performax_hub.db`
- 키워드 트렌드 히스토리: 최근 20개
- 키워드 쿼리 히스토리: 최근 20개
- 구글 시트 URL: 자동 저장 (앱 재시작 시 자동 불러오기)

---

## 파일 구조

```
performax_hub/
├── app.py                        — Flask 서버
├── build.bat                     — EXE 빌드
├── README.md
├── templates/
│   ├── base.html                 — 사이드바 공통 레이아웃
│   ├── keyword_trend.html        — 키워드 트렌드 분석
│   ├── keyword_query.html        — 키워드 쿼리 조회
│   └── utm_builder.html          — UTM 빌더
└── static/
    └── style.css                 — 공통 스타일
```

---

## 주의사항

- 사내 VPN 환경 대응을 위해 SSL 검증이 비활성화되어 있습니다. (`verify=False`)
- API 키는 `app.py`에 하드코딩되어 있으므로 외부에 공유하지 마세요.
- 구글 시트 UTM 규칙 수정 시 앱에서 **불러오기**를 다시 눌러야 반영됩니다.
