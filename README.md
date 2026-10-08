# 선재·이형재 인발 종합 산출 도구

냉간인발(원형 → 사각·육각) 공정 계산기입니다.

- 감면율과 예상 모서리 R (실측 14본·56코너로 보정한 코너 갭 모델, 자연 R ↔ 다이스 R 경계 표시)
- 인발력 · 호기별 설비 검증 (설비 능력 95% 기준)
- 규격별 중량, 환산 직진도
- 실측 R DB와 모델 재보정

## 실행

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Streamlit Community Cloud에서는 Main file path를 `streamlit_app.py`로 지정합니다.

> 사내 실측 데이터가 코드에 포함되어 있으므로 저장소는 **Private**으로 유지하세요.
