# 📊 학원 성적 분석 Streamlit 앱

엑셀 파일을 업로드하면 학생별 / 반별 / 과목별 성적을 자동으로 분석해주는 웹 앱입니다.
학원에서 성적 관리 및 상담 자료로 활용할 수 있습니다.

---

## 🚀 주요 기능

* 📁 엑셀 / CSV 파일 업로드
* 🔎 학년 / 반 / 시험명 필터
* 👤 학생 이름 검색
* 📊 과목별 평균 자동 계산
* 🧮 학생별 총점 / 평균 계산
* 📈 과목별 평균 그래프
* 👤 학생별 성적 그래프
* 🏫 반별 평균 분석
* 🏆 학생 순위표 자동 생성
* 📥 CSV 다운로드

---

## 🖥 실행 방법

### 1. 필요한 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 2. 앱 실행

```bash
streamlit run app.py
```

또는 (실행이 안될 경우)

```bash
python -m streamlit run app.py
```

---

## 📁 파일 구성

```text
score_app
 ├─ app.py                # 메인 프로그램
 ├─ requirements.txt     # 필요 라이브러리
 └─ README.md            # 설명 파일
```
