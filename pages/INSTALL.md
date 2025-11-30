# 설치 가이드

## Windows 환경 설치 방법

### 1. Python 버전 확인
```bash
python --version
```
Python 3.8 이상이 필요합니다.

### 2. pip 업그레이드
```bash
python -m pip install --upgrade pip
```

### 3. 패키지 설치

#### 방법 1: requirements.txt 사용 (권장)
```bash
pip install -r requirements.txt
```

#### 방법 2: 단계별 설치 (에러 발생 시)
만약 `requirements.txt`로 설치 중 에러가 발생한다면, 다음 순서로 단계별 설치를 시도하세요:

```bash
# 기본 패키지 먼저 설치
pip install streamlit numpy pandas networkx requests geopy scikit-learn

# 지도 관련 패키지
pip install folium streamlit-folium

# 지리 공간 데이터 처리 패키지
pip install shapely pyproj geopandas

# OSMnx (OpenStreetMap 데이터 처리)
pip install osmnx
```

### 4. 설치 확인
```bash
python -c "import streamlit; import osmnx; import folium; print('설치 성공!')"
```

## 일반적인 에러 해결 방법

### 에러 1: "Microsoft Visual C++ 14.0 is required"
**해결 방법:**
- [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) 설치
- 또는 미리 컴파일된 wheel 파일 사용:
  ```bash
  pip install --only-binary :all: osmnx
  ```

### 에러 2: "Could not find a version that satisfies the requirement"
**해결 방법:**
- Python 버전 확인 (3.8 이상 필요)
- pip 업그레이드:
  ```bash
  python -m pip install --upgrade pip
  ```

### 에러 3: OSMnx 설치 실패
**해결 방법:**
- Conda 사용 (권장):
  ```bash
  conda install -c conda-forge osmnx
  ```
- 또는 의존성 먼저 설치:
  ```bash
  pip install geopandas shapely pyproj
  pip install osmnx
  ```

### 에러 4: 네트워크 타임아웃
**해결 방법:**
- 타임아웃 시간 증가:
  ```bash
  pip install --default-timeout=100 -r requirements.txt
  ```
- 또는 미러 사이트 사용:
  ```bash
  pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
  ```

## 가상 환경 사용 (권장)

프로젝트별로 독립된 환경을 사용하는 것을 권장합니다:

```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화 (Windows)
venv\Scripts\activate

# 가상 환경 활성화 (Linux/Mac)
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

## Streamlit Cloud 배포 시

Streamlit Cloud는 자동으로 `requirements.txt`를 읽어 패키지를 설치합니다.
별도의 설정 파일(`packages.txt` 등)은 필요하지 않습니다.

