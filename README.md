# Football Manager Web

웹 기반 축구 팀 매니징 게임입니다. Python 게임 로직을 Flask API와 HTML/CSS/JavaScript 프런트엔드로 감싸서 브라우저에서 바로 플레이할 수 있게 정리했습니다.

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

Windows에서는 `풋볼매니저_실행.bat`을 실행해도 됩니다.

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
