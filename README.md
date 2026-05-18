# Football Manager Web

Python으로 만든 풋볼 매니저 게임을 Flask 기반 웹 서비스 게임으로 정리한 프로젝트입니다.

## 주요 기능

- 새 시즌 생성
- 포메이션 선택: 4-3-3, 4-2-4, 3-5-2, 5-3-2
- 전술 선택: 균형, 공격, 수비
- 경기 시뮬레이션
- 리그 순위표와 최근 경기 결과 표시
- 브라우저에서 바로 플레이하는 웹 UI

## 실행 방법

```bash
pip install -r requirements.txt
python app.py
```

브라우저에서 `http://localhost:5000`으로 접속합니다.

## 프로젝트 구조

```text
.
├── app.py
├── config.py
├── game_engine.py
├── player.py
├── team.py
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── game.js
```

## API

- `POST /api/game/start`: 새 게임 시작
- `GET /api/game/<game_id>/status`: 게임 상태 조회
- `POST /api/game/<game_id>/formation`: 포메이션과 전술 저장
- `POST /api/game/<game_id>/match`: 경기 진행
- `POST /api/game/<game_id>/reset`: 시즌 기록 초기화

## GitHub 관리

처음 업로드할 때:

```bash
git init
git add .
git commit -m "Initial web football manager"
git branch -M main
git remote add origin https://github.com/<your-id>/football-manager-web.git
git push -u origin main
```
